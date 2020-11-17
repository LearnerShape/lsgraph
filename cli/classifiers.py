"""Classification functionality"""
import click
from datetime import datetime
from collections import defaultdict
import importlib
import json
import os
import pdb
import sys
from zipfile import ZipFile

from .config import Config
from .crawlers import Crawlers


class Classifiers:
    """Load all classifiers from the plugin directories"""
    classifiers = {}


    @classmethod
    def load(cls, plugin_directories):
        """Load all classifiers from the plugin directories"""
        for plugin_directory in plugin_directories:
            cls._load(cls, os.path.join(plugin_directory, 'models'))


    def _load(cls, plugin_directory):
        """Find and load all crawlers in one directory"""
        f = os.listdir(plugin_directory)
        f = [i for i in f if i.endswith('.py')]
        # Convert names
        def convert_names(s):
            s = s[:-3]
            return (s, ''.join([i[0].upper() + i[1:] for i in s.split('_')]))
        f = [convert_names(i) for i in f]
        # Change path
        current_path = sys.path[:]
        sys.path = [plugin_directory] + current_path

        # Load modules
        for mod,c in f:
            model = importlib.import_module(mod).__getattribute__(c)
            cls.classifiers[mod] = model

        # Change path back
        sys.path = current_path



def begin_classification(organisation, model, provider, crawl, clean):
    """Collect classification task and begin

    Organisation: Always needed to get skills. If provided alone get model
                  and providers from config and use latest crawls
    Model:        If provided, override organisation config
    Provider:     If provided, override organisation config
    Crawl:        If provided, use instead of latest
    Clean:        Create a new analysis from scratch rather than resuming
                  an existing model"""
    click.echo(organisation)
    click.echo(model)
    click.echo(provider)
    click.echo(crawl)
    click.echo(clean)
    # Get skills from database for organisation(s)
    skills = get_skills(organisation)
    skills = ["|".join([j['name'] for j in i]) for i in skills]
    # Get model
    classifier = Classifiers.classifiers[model]
    # Get all courses
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
    classifier = classifier(Config.active['results_dir'], desired_crawlers, skills, clean)
    classifier.run()


def get_skills(organisation):
    """Fetch all skills for an organisation from the database"""
    # Get root ID
    graph_tag = Config.active['organisations'][organisation]['graph']
    db = Config.get_db_cursor()
    db.execute('SELECT root_id FROM graphs WHERE graph_tag = %s',
               [graph_tag, ])
    root_id = db.fetchone()[0]
    # Get all skills
    db.execute('SELECT id,name FROM skills WHERE personal = False')
    skills = db.fetchall()
    skills = {i[0]:i[1] for i in skills}
    # Get all skill links/includes
    db.execute('SELECT id,subject_id,object_id FROM skill_includes WHERE personal = False')
    skill_includes = db.fetchall()
    # Build full paths for all skills from root
    skill_connections = defaultdict(list)
    for s_i in skill_includes:
        skill_connections[s_i[1]].append(s_i[2])
    skill_paths = r_build_paths(skills, skill_connections, [], root_id, [])
    return skill_paths


def r_build_paths(skills, skill_connections, all_paths,
                  subject_id, current_path):
    """Recursively build all skill paths from the root ID"""
    children = skill_connections[subject_id]
    for child in children:
        try:
            current_node = {'id':child,'name':skills[child]}
            new_path = current_path[:] + [current_node]
            all_paths.append(new_path)
            all_paths = r_build_paths(skills, skill_connections, all_paths,
                                  child, new_path)
        except:
            click.echo('Issue constructing path for skill {0}'.format(child))
    return all_paths


class GenericClassifier:
    def __init__(self, results_dir, crawlers, skills, clean=False):
        """Initialize the classifier"""
        self.results_dir = results_dir
        self.skills = skills
        self.skills.sort()
        self.crawlers = crawlers
        if not clean:
            identifier = self._find_classifier()
        if not identifier:
            self._initialise()


    @property
    def prefix(self):
        return "classify_{0}_".format(self.name)


    def _initialise(self):
        """Configure classifier storage"""
        crawlers = [i.identifier for i in self.crawlers]
        crawlers.sort()
        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        self.identifier = "{0}{1}".format(self.prefix, dt)
        self.fn = "{0}.zip".format(self.identifier)
        with ZipFile(os.path.join(self.results_dir, self.fn), 'x') as z:
            with z.open('skills.json', 'w') as fp:
                fp.write(json.dumps(self.skills).encode('utf-8'))
            with z.open('crawlers.json', 'w') as fp:
                fp.write(json.dumps(crawlers).encode('utf-8'))
        self.status = ""


    def _find_classifier(self):
        """Check whether any existing classifier runs match this one"""
        candidates = [i for i in os.listdir(self.results_dir) if i.startswith(self.prefix)]
        candidates.sort(reverse=True)
        crawlers = [i.identifier for i in self.crawlers]
        crawlers.sort()
        for candidate in candidates:
            with ZipFile(os.path.join(self.results_dir, candidate)) as z:
                with z.open('skills.json') as fp:
                    c_skills = json.loads(fp.read())
                with z.open('crawlers.json') as fp:
                    c_crawlers = json.loads(fp.read())
                status = ''
                if 'status' in z.namelist():
                    with z.open('status') as fp:
                        status = fp.read().strip()
            if (c_skills == self.skills) and (c_crawlers == crawlers):
                self.fn = candidate
                self.identifier = candidate[:-4]
                self.status = status
                return self.identifier


    def run(self):
        """Classify courses using model"""
        raise Exception('Not Implemented')
