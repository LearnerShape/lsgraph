"""Load courses and scores"""
import click
from collections import defaultdict
from datetime import datetime
import json
import pdb
from psycopg2.extras import execute_batch


from .config import Config
from .crawlers import Crawlers, h
from .classifiers import get_skills, Classifiers

def load_courses(organisation, provider, crawl, clean):
    """Load all courses into the target database

    Organisation: Always needed to get skills. If provided alone get
                  providers from config and use latest crawls
    Provider:     If provided, override organisation config
    Crawl:        If provided, use instead of latest
    Clean:        Update courses that have already been loaded"""
    # Get all crawlers/courses
    if provider:
        desired_crawlers = provider.split(',')
    elif crawl:
        click.echo('Choosing specific crawls not yet implemented')
        return
    else:
        desired_crawlers = Config.active['organisations'][organisation]['providers']
    desired_crawlers = [Crawlers.crawlers[i] for i in desired_crawlers]
    desired_crawlers = [i(Config.active['results_dir']) for i in desired_crawlers]
    desired_crawlers = [i.get_crawl(i.list()[-1]) for i in desired_crawlers]
    #for d in desired_crawlers:
    #    click.echo(d.crawler.name)
    # Get existing courses
    db = Config.get_db_cursor()
    db.execute('SELECT id,platform,alt_id FROM courses')
    def lower_f(i):
        if not i:
            return ''
        return i.lower()
    existing_courses = {(lower_f(i[1]),i[2]):i[0] for i in db.fetchall()}
    #existing_platform = set([i[0] for i in existing_courses.keys()])
    #platform_count = {i:len([j for j in existing_courses if j[0] == i]) for i in existing_platform}
    # Load new courses
    new_count = 0
    existing_count = 0
    update_query = """UPDATE courses SET name=%(name)s,
                        type=%(type)s, platform=%(platform)s,
                        duration=%(duration)s, url=%(url)s,
                        duration_code=%(duration_code)s, alt_id=%(alt_id)s,
                        description=%(description)s,
                        short_description=%(short_description)s,
                        weekly_effort=%(weekly_effort)s,
                        modified_at=%(modified_at)s
                        WHERE id=%(existing_id)s;"""
    update_batch = []
    new_query = """INSERT INTO courses (name,
                    type, platform, duration, url, duration_code,
                    alt_id, description, short_description,
                    weekly_effort) VALUES (%(name)s, %(type)s, %(platform)s,
                    %(duration)s, %(url)s, %(duration_code)s, %(alt_id)s,
                    %(description)s, %(short_description)s,
                    %(weekly_effort)s);"""
    new_batch = []
    def process_batch(q, batch, force=False, batch_size=500):
        if force or (len(batch) > batch_size):
            execute_batch(db, q, batch)
            Config.db_conn.commit()
            batch = []
        return batch
    load_time = 0
    parse_time = 0
    for crawl in desired_crawlers:
        crawler_name = crawl.crawler.name
        with click.progressbar(crawl.list_courses().items(),
                               label="Processing {0}".format(crawler_name)) as bar:
            for identifier, h_id in bar:
                if ((crawler_name.lower(), identifier) in existing_courses) and not clean:
                    continue
                c = crawl.get_course(h_id)
                load_time += c.load_time
                parse_time += c.parse_time
                if not c.is_active:
                    continue
                course = c.to_DB
                #click.echo(course['platform'])
                if (course['platform'].lower(), course['alt_id']) in existing_courses:
                    existing_count += 1
                    if clean:
                        # Update existing record
                        course['modified_at'] = datetime.now()
                        course_id = (lower_f(course['platform']), course['alt_id'])
                        course['existing_id'] = existing_courses[course_id]
                        update_batch.append(course)
                else:
                    new_count += 1
                    # Add new record
                    course['created_at'] = datetime.now()
                    course['modified_at'] = datetime.now()
                    new_batch.append(course)
                update_batch = process_batch(update_query, update_batch)
                new_batch = process_batch(new_query, new_batch)
            click.echo(load_time)
            click.echo(parse_time)
    update_batch = process_batch(update_query, update_batch, force=True)
    new_batch = process_batch(new_query, new_batch, force=True)

    db.execute('SELECT id,platform,alt_id FROM courses')
    existing_courses = {(i[1],i[2]):i[0] for i in db.fetchall()}
    return existing_courses


def load_scores_from_results(organisation, results):
    db = Config.get_db_cursor()
    existing_courses = get_courses(db)
    skills = get_skill_map(db, organisation)

    with open(results) as fp:
        good_course_scores = json.load(fp)

    child_paths = get_child_paths(skills)
    for skill_path in skills.keys():
        skill_id = skills[skill_path]
        # Delete old scores
        db.execute("DELETE FROM course_scores WHERE skill_id = %s AND score_type NOT LIKE 'level:%%'",
                   [skill_id,])
        # Load new scores
        courses_loaded = 0
        course_scores = good_course_scores.get(skill_path, {})
        for course, score in course_scores.items():
            if course.lower() not in existing_courses:
                continue
            course_id = existing_courses[course.lower()]
            load_score(db, skill_id, course_id, score)
            courses_loaded += 1
        if courses_loaded < 15:
            child_scores = {}
            for child_path in child_paths[skill_path]:
                child_scores.update(good_course_scores.get(child_path, {}))
            for course, score in child_scores.items():
                if course.lower() not in existing_courses:
                    continue
                course_id = existing_courses[course.lower()]
                load_score(db, skill_id, course_id, score/2)
                courses_loaded += 1
        Config.db_conn.commit()


def load_levels_from_results(organisation, results):
    """Load manually reviewed predicted level scores"""
    db = Config.get_db_cursor()
    existing_courses = get_courses(db)
    skills = get_skill_map(db, organisation)

    with open(results) as fp:
        good_course_scores = json.load(fp)

    for skill_path in skills.keys():
        skill_id = skills[skill_path]
        # Delete old scores
        db.execute("DELETE FROM course_scores WHERE skill_id = %s AND score_type LIKE 'level:%%'",
                   [skill_id,])
        # Load new scores
        course_scores = good_course_scores.get(skill_path, {})
        for course, score in course_scores.items():
            if course.lower() not in existing_courses:
                continue
            course_id = existing_courses[course.lower()]
            load_score(db, skill_id, course_id, score, "level:manual")
        Config.db_conn.commit()


def load_scores_from_model(organisation, model, num_to_load=20):
    """Load scores from a model"""
    db = Config.get_db_cursor()
    existing_courses = get_courses(db)
    skills = get_skill_map(db, organisation)
    skill_paths = list(skills.keys())
    child_paths = get_child_paths(skills)

    # Get model
    model = Classifiers.classifiers[model]
    desired_crawlers = Config.active['organisations'][organisation]['providers']
    desired_crawlers = [Crawlers.crawlers[i] for i in desired_crawlers]
    desired_crawlers = [i(Config.active['results_dir']) for i in desired_crawlers]
    desired_crawlers = [i.get_crawl(i.list()[-1]) for i in desired_crawlers]
    classifier = model(Config.active['results_dir'], desired_crawlers, skill_paths)

    # Load scores
    with click.progressbar(skill_paths, label="Processing skills") as bar:
        for skill_path in bar:
            skill_id = skills[skill_path]
            # Delete old scores
            db.execute('DELETE FROM course_scores WHERE skill_id = %s',
                       [skill_id,])
            # Load new scores
            courses_to_load = []
            for course, score in classifier.courses_for_skill(skill_path):
                if course not in existing_courses:
                    continue
                course_id = existing_courses[course]
                if isinstance(score, list):
                    score = sum(score) / len(score)
                courses_to_load.append((course_id, score))
            courses_to_load.sort(key=lambda x:x[1], reverse=True)
            for course_id, score in courses_to_load[:num_to_load]:
                load_score(db, skill_id, course_id, score)
    Config.db_conn.commit()


def get_courses(db):
    db.execute('SELECT id,platform,alt_id FROM courses')
    def lower_f(i):
        if not i:
            return ''
        return i.lower()
    existing_courses = {'{0}|{1}'.format(lower_f(i[1]),
                                         h(i[2] if i[2] else '')):i[0] for i in db.fetchall()}
    return existing_courses


def get_skill_map(db, organisation):
    skills = get_skills(organisation)

    def build_path(s):
        if len(s) == 1:
            return s[0]['name']
        return '|'.join([i['name'] for i in s])

    skills = {build_path(i):i[-1]['id'] for i in skills}
    return skills


def get_child_paths(skills):
    child_paths = defaultdict(list)
    for p in skills.keys():
        branch, _, leaf = p.rpartition('|')
        child_paths[branch].append(p)
    return child_paths


def load_score(db, skill_id, course_id, score, score_type="simple_avg"):
    q = """INSERT INTO course_scores (course_id, skill_id,
            score, score_type, created_at, updated_at)
            VALUES (%(course_id)s, %(skill_id)s, %(score)s,
            %(score_type)s, %(created_at)s, %(updated_at)s);"""
    vars = {'skill_id':skill_id,
            'course_id':course_id,
            'score':score,
            'score_type':score_type,
            'created_at':datetime.now(),
            'updated_at':datetime.now()}
    db.execute(q, vars)
