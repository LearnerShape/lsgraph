# Copyright (C) 2019-2020  Learnershape and contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Responsible for learning resource selection and scheduling"""
from bisect import bisect
from copy import deepcopy
from itertools import accumulate
from math import ceil, floor
import random
from datetime import datetime, timedelta
from dateutil.parser import parse
import pytz
from .models import CourseScore, Course
from pdb import set_trace

course_columns = ['id','name', 'type', 'provider', 'platform',
                  'duration', 'duration_code', 'url', 'description',
                  'short_description', 'weekly_effort']
course_converters = {'duration': lambda x:int(float(x)),
                     'weekly_effort':lambda x:int(x) if x else 1}



def actual_query(q):
    st = q.statement
    from sqlalchemy.dialects import postgresql
    return st.compile(dialect=postgresql.dialect(),
                                 compile_kwargs={'literal_binds': True})
def t0():
    import time
    return time.time()

def t1(_t0):
    import time
    _t1 = time.time()
    print('finish '+str(round(_t1-_t0,3)))


def normalize_datetime(date):
    """Convert a datetime string to a datetime object

    Add a default timezone if no current timezone"""
    dt = parse(date)
    if dt.tzinfo == None:
        dt = dt.astimezone(pytz.utc)
    return dt

def normalize_schedule(schedule):
    """Convert keys to ints and dates to datetimes"""
    new_schedule = {}
    conv = lambda i,j: normalize_datetime(j) if i in ['start', 'end'] else j
    for sid,course in schedule.items():
        new_schedule[int(sid)] = {k:conv(k,v) for k,v in course.items()}
    return new_schedule


def update_constraints(d,n):
    """Merge a default set of constraints with new constraints"""
    for k,v in d.items():
        if k in n:
            if isinstance(v, dict):
                d[k] = update_constraints(v,n[k])
            else:
                d[k] = n[k]
    return d


def normalize_constraints(constraints):
    if 'article' in constraints['sources']['type']['whitelist']:
        constraints['sources']['type']['whitelist'].extend(['article/blog'])
    for k in ['maximum_total', 'maximum_per_course']:
        constraints['cost'][k] = int(constraints['cost'][k])
    for k in ['target_duration',
              'maximum_duration',
              'target_weekly_effort',
              'maximum_weekly_effort',
              'minimum_course_duration',
              'maximum_course_duration']:
        constraints['time'][k] = int(constraints['time'][k])
    return constraints


default_constraints = {'sources':{'type':{'whitelist':['course-online',
                                               'course-offline',
                                               'article',
                                               'video',
                                               'audio',
                                               'MOOC',
                                               'Online L&D',
                                               'article-blog'],
                                  'blacklist':[]}},
               'cost':{'maximum_total':1,
                       'maximum_per_course':1},
               'time':{'target_weekly_effort':5,
                       'maximum_weekly_effort':5,
                       'target_duration':12,
                       'maximum_duration':16,
                       'minimum_course_duration':1,
                       'maximum_course_duration':60*60*24*365}}


def weighted_course_score_identity(scores):
    return scores


def weighted_course_score_rank(scores):
    m = len(scores)
    return [m-i for i in range(m)]


def weighted_course_score_rank2(scores):
    weights = [100,100,100,50,50,10,8,6,4,2]
    if len(weights) < len(scores):
        weights.extend([1 for i in range(len(scores) - len(weights))])
    return weights[:len(scores)]


def weighted_course_duration_blank(courses, constraints):
    durations = []
    for c in courses:
        durations.append(0)
    return durations


class PathwayService:
    """Gathers courses based on skills gap and suggests schedule"""


    def __init__(self, graph, pointA, pointB, constraints={},
                 schedule_population=500,
                 course_score_weight=1,
                 course_duration_weight=1,
                 course_score_func='rank2',
                 course_duration_func='blank'):
        """Set up state

        graph: Graph object
        pointA: List of skill ids the learner currently has
        pointB: List of skill ids the learner wants to develop"""
        self.graph = graph
        self.pointA = pointA
        self.pointB = pointB
        self.courses = {}
        self.constraints = update_constraints(deepcopy(default_constraints),
                                              constraints)
        self.constraints = normalize_constraints(self.constraints)
        self.schedule_population = schedule_population
        self.course_score_weight = course_score_weight
        self.course_duration_weight = course_duration_weight
        self.course_score_func = course_score_func
        self.course_duration_func = course_duration_func

        self.skill_gap = []


    def identify_skill_gap(self):
        """Identify the missing skills"""
        skill_gap = []
        skill_rank = {'no knowledge':0,
                      'beginner':1,
                      'intermediate':2,
                      'advanced':3,
                      'expert':4}
        for skill in self.pointB:
            # set_trace()
            if skill not in self.pointA:
                skill_gap.append(skill)
            elif skill_rank[self.pointA[skill]] <= 1:
                skill_gap.append(skill)
            elif skill_rank[self.pointA[skill]] < skill_rank[self.pointB[skill]]:
                skill_gap.append(skill)
        self.skill_gap = skill_gap
       
        return skill_gap


    def get_skill_scores(self):
        """Load the scores from the database for the skill gap"""
        courses = self._get_scores_for_skills(self.skill_gap, 10)
        weighted_courses = self._get_weighted_courses(courses)
        self.skills = weighted_courses
        for k in self.skills.keys():
            self.skills[k].sort(key=lambda x:x[1], reverse=True)


    def get_best_schedule(self, schedule_start):
        """Selects the best courses and recommends a learning schedule

        max_hours_per_week:  The maximum number of hours to schedule per week
        weeks_to_plan:       Target number of weeks to assign courses within
        """
        print('-- Pathway service - get_best_schedule')
        options = self._get_candidate_course_selections(n=self.schedule_population)
        max_hours_per_week = self.constraints['time']['maximum_weekly_effort']
        weeks_to_plan = self.constraints['time']['maximum_duration']
        scores = []
        for best, course_skills in options:
            schedule = self._schedule_courses(best,
                                max_hours_per_week=max_hours_per_week,
                                weeks_to_plan=weeks_to_plan)
            if not schedule:
                schedule_score = 0
            else:
                schedule_score = self._score_schedule(best,
                                                      course_skills,
                                                      schedule)
            scores.append([best, course_skills, schedule, schedule_score])
        scores.sort(key=lambda x:x[3], reverse=True)
        best, course_skills, schedule, score = scores[0]
        if schedule == None:
            raise Exception('No valid schedule could be found')
        external_schedule = self._convert_schedule_external(best,
                                                            course_skills,
                                                            schedule,
                                                            schedule_start)



        valid, msg = self.validate_schedule(external_schedule)
        if external_schedule.values():
          schedule_end = max([i['end'] for i in external_schedule.values()])
        else:
          schedule_end = schedule_start
        to_return = {'courses':external_schedule,
                     'schedule_start':schedule_start,
                     'schedule_end':schedule_end,
                     'valid':valid,
                     'valid_msg':msg}
        return to_return


    def courses_for_skill(self,skill_ids,n_courses=10,
                          n_courses_per_skill=10):
        """Return courses for a selected skill"""
        skills = self._get_scores_for_skills(skill_ids)
        for k in skills.keys():
            skills[k].sort(key=lambda x:x[1], reverse=True)
        to_return = []
        for n,i in enumerate(zip(*skills.values())):
            if n >= n_courses_per_skill:
                continue
            # Interleave the next best courses for each skill
            # i.e. for skills A and B, return A2, B2, A3, B3, etc
            for j in i:
                new_course = j[0][1]
                skills = [{"id":j[0][0],
                           "name":self.graph.skills[j[0][0]]["name"]}]
                new_course['skills'] = skills
                to_return.append(new_course)
                if len(to_return) >= n_courses:
                    return {'courses':to_return}
        return {'courses':to_return}


    def alternative_courses_for_skills(self, schedule, course_id,
                                       n_courses=10):
        """Return alternatives for a selected course"""
        # set_trace()
        skill_ids = []

        if course_id in schedule:
          skill_ids = [i['id'] for i in schedule[course_id]['skills']]
        skills = self._get_scores_for_skills(skill_ids)
        for k in skills.keys():
            skills[k].sort(key=lambda x:x[1], reverse=True)
        to_return = []
        for n,i in enumerate(zip(*skills.values())):
            # Interleave the next best courses for each skill
            # i.e. for skills A and B, return A2, B2, A3, B3, etc
            for j in i:
                new_course = j[0][1]
                if new_course['id'] in schedule:
                    # If a course is already being suggested ignore it
                    # TODO: Potentially alert learner that an existing
                    # course can be used
                    continue
                # if j[0][0] not in self.graph.skills:
                #   set_trace()
                skills = [{"id":j[0][0],
                           "name":self.graph.skills[j[0][0]]["name"]}]
                new_course['skills'] = skills
                to_return.append(new_course)
                if len(to_return) >= n_courses:
                    return {'courses':to_return}
        return {'courses':to_return}


    def validate_schedule(self, schedule):
        """Check whether a schedule meets the set constraints"""
        if not schedule:
          msg = ['Calendar is empty!']
          valid = False
          return valid,msg
        schedule = normalize_schedule(schedule)
        valid = True
        msg = []
        time_delta = timedelta(days=7)
        # Check whether schedule is too long
        schedule_start = min([i['start'] for i in schedule.values()])
        schedule_end = max([i['end'] for i in schedule.values()])
        wks = ceil((schedule_end - schedule_start)/time_delta) + 1
        if wks > self.constraints['time']['maximum_duration']:
            valid = False
            msg.append("Courses have been scheduled over too many weeks")
        # Check whether too many hours scheduled during any week
        wk_starts = [schedule_start+time_delta*i for i in range(wks)]
        weekly_total = [0] * wks
        for c in schedule.values():
            c_start = bisect(wk_starts, c['start'])-1
            for i,h in enumerate(c['time_per_week']):
                weekly_total[c_start+i] += h
        for i,(h,s) in enumerate(zip(weekly_total, wk_starts)):
            if h > self.constraints['time']['maximum_weekly_effort']:
                valid = False
                msg.append("Too many hours scheduled for week {0} ({1})".format(i+1,s.isoformat()))
        # Check whether all skills are taught
        all_skills = []
        skill_map = {}
        for c in schedule.values():
            all_skills.extend([i['id'] for i in c['skills']])
            skill_map.update({i['id']:i['name'] for i in c['skills']})
        for skill in self.skill_gap:
            if skill not in all_skills:
                valid = False
                # Include skill name if available or id if not
                s_name = skill_map.get(skill, "ID:{0}".format(skill))
                msg.append("The skill {0} is not taught".format(s_name))
        return valid, msg


    def _get_scores_for_skills(self, skill_ids, top_n=20):
        """Get scores relevant for a skill"""
        session = self.graph.Session()
        print('q')
        t = t0()
        skills = {}
        
        try:
          # This is doing a full INNER JOIN between course_scores and courses, which is huge
            query = session.query(CourseScore, Course). \
                filter(CourseScore.course_id == Course.id). \
                filter(CourseScore.skill_id.in_(skill_ids))
            type_whitelist = self.constraints['sources']['type']['whitelist']
            if type_whitelist != []:
                query = query.filter(Course.type.in_(type_whitelist))
            query = query.order_by(CourseScore.score.desc())
            print('-----Actual query:')
            print(actual_query(query))

            for score, course in query:
                if score.skill_id not in skills:
                    skills[score.skill_id] = []
                if len(skills[score.skill_id]) >= top_n:
                    continue
                course_out = {k:course_converters.get(k, lambda x:x)(course.__dict__[k]) for k in course_columns}
                max_duration_weeks = self.constraints['time']['maximum_duration']
                max_weekly_effort = self.constraints['time']['maximum_weekly_effort']
                min_c_duration = self.constraints['time']['minimum_course_duration']
                max_c_duration = self.constraints['time']['maximum_course_duration']
                if course_out['duration_code'] == 'W':
                    if course_out['duration'] > max_duration_weeks:
                        continue
                    if course_out['weekly_effort'] > max_weekly_effort:
                        continue
                    d = 60*60*24*7*course_out['duration']
                    if max_c_duration < d:
                        continue
                    if min_c_duration > d:
                        continue
                    course_out['duration_in_seconds'] = course_out['duration']*60*60*24*7
                elif course_out['duration_code'] == 'S':
                    if max_c_duration < course_out['duration']:
                        continue
                    if min_c_duration > course_out['duration']:
                        continue
                    course_out['duration_in_seconds'] = course_out['duration']
                skills[score.skill_id].append([(score.skill_id, course_out),
                                               score.score])
            session.commit()
        except:
            session.rollback()
            print("Error loading skill scores")
            raise
        finally:
            session.close()
        t1(t)
        return skills


    def _get_courses(self, course_ids):
        """Get course details from ids"""
        session = self.graph.Session()
        new_ids = [i for i in course_ids if i not in self.courses]
        if new_ids:
            courses = {}
            try:
                query = session.query(Course).filter(Course.id.in_(new_ids))
                for course in query:
                    courses[course.id] = {k:course_converters.get(k, lambda x:x)(course.__dict__[k]) for k in course_columns}
                session.commit()
            except:
                session.rollback()
                print("Error loading course details")
                raise
            finally:
                session.close()
            self.courses.update(courses)
        courses = {i:self.courses[i] for i in course_ids}
        return courses


    def _get_candidate_course_selections(self, n):
        """Get multiple possible course selections to meet skill gap"""
        options = []
        for i in range(n):
            options.append(self._get_candidate_course_selection())

        return options


    def _get_candidate_course_selection(self):
        """Create a list of courses that fill the skill gap

        Courses are chosen based on the top scoring course for each skill"""
        def weighted_random_choice(courses):
            weights = [weight for c,score,duration,weight in courses]
            cumdist = list(accumulate(weights))
            point = random.random() * cumdist[-1]
            return courses[bisect(cumdist, point)]

        course_selection = []
        course_skills = {}
        course_map = {}
        for skill in self.skill_gap:
            course_options = self.skills.get(skill, None)
            if course_options == None:
                continue
            if course_options == []:
                continue
            top_match = weighted_random_choice(course_options)
            course_id = top_match[0]['id']
            course_map[course_id] = top_match[0]
            if course_id not in course_selection:
                # Avoid adding the same course multiple times
                course_selection.append(course_id)
            # Keep track of all skills that recommended a course
            if course_id not in course_skills:
                course_skills[course_id] = []
            course_skills[course_id].append(skill)
        missing_courses = [i for i in course_selection if i not in course_map]
        course_map.update(self._get_courses(missing_courses))
        course_selection = [course_map[i] for i in course_selection]
        return course_selection, course_skills


    def _schedule_courses(self, selection, max_hours_per_week,
                                min_allocation=1, weeks_to_plan=12):
        """Optimally schedule a collection of courses

        Returns: A list of dictionaries containing id, start, end, hrs/wk"""
        weekly_slots = [[] for i in range(weeks_to_plan)]
        current_week = 0
        for course in selection:
            weekly_slots = self._add_course(weekly_slots, course)
        schedule = []
        for week in weekly_slots:
            counts = {}
            for course in week:
                if course["id"] not in counts:
                    counts[course["id"]] = 0
                counts[course["id"]] += 1
            schedule.append(counts)

        return schedule


    def _score_schedule(self, courses, skills, schedule):
        """Evaluate the suitability of a schedule

        Higher is better"""
        # Check for any missed skills
        taught_skills = []
        for s in skills.values():
            taught_skills.extend(s)
        missed_skills = [i for i in self.skill_gap if i not in taught_skills]
        missed_penalty = len(missed_skills) / len(self.skill_gap)
        # Score length of schedule
        the_list = [i+1 for i,j in enumerate(schedule) if j]
        if len(the_list) == 0:
            return 0 - 10*missed_penalty
        target_len = self.constraints['time']['target_duration']
        max_len = self.constraints['time']['maximum_duration']
        schedule_len = max(the_list)
        expected_len = 0.5 * len(self.skill_gap)
        expected_len = expected_len if expected_len < target_len else target_len
        if schedule_len >= target_len:
            length_penalty = 1 - (schedule_len - target_len) / max_len
        elif target_len > schedule_len >= expected_len:
            length_penalty = 1
        elif schedule_len < expected_len:
            length_penalty = 1 - (expected_len - schedule_len) / expected_len
        return length_penalty - 10*missed_penalty


    def _get_weighted_courses(self, scored_courses):
        """Provide a weight for the suitability of a course"""
        score_funcs = {'identity':weighted_course_score_identity,
                       'rank':weighted_course_score_rank,
                       'rank2':weighted_course_score_rank2,
        }
        duration_funcs = {'blank':weighted_course_duration_blank}
        score_func = score_funcs[self.course_score_func]
        duration_func = duration_funcs[self.course_duration_func]
        output = {}
        for skill_id, courses in scored_courses.items():
            scores = score_func([i for _,i in courses])
            durations = duration_func([i for (_,i),_ in courses],
                                      self.constraints)
            weights = [s*self.course_score_weight+d*self.course_duration_weight for s,d in zip(scores, durations)]
            output[skill_id] = list(zip([i for (_,i),_ in courses],
                                        scores, durations, weights))
        return output


    def _convert_schedule_external(self, courses, course_skills,
                                   schedule, schedule_start):
        """Convert the internal schedule representation to
        the output format

        courses:
        course_skills:
        schedule:
        schedule_start:"""
        course_ids = [i["id"] for i in courses]
        course_map = {i['id']:i for i in courses}
        to_return = {}
        for c_id in course_ids:
            wks = [i for i,j in enumerate(schedule) if c_id in j]
            if wks == []:
                continue
            start = min(wks)
            end = max(wks)+1
            output = course_map[c_id]
            if 'start' in output:
                if isinstance(output['start'], str):
                  output['start'] = parse(output['start'])
                if isinstance(schedule_start, str):
                  schedule_start = parse(schedule_start)
                offset = (output['start']-schedule_start) % timedelta(days=7)
            else:
                offset = timedelta(0)
            start_ts = schedule_start + start*timedelta(days=7) + offset
            end_ts = schedule_start + end*timedelta(days=7) + offset
            time_per_week = [schedule[i][c_id] for i in range(start, end)]
            skills = [{"id":sid,
                       "name":self.graph.skills[sid]["name"]}  for sid in \
                      course_skills[c_id] if sid in self.graph.skills]
            output.update({"start":start_ts.isoformat(),
                    "end":end_ts.isoformat(),
                    "time_per_week":time_per_week,
                    "axis":"A",
                    "skills":skills,
                    })
            to_return[c_id] = output
        return to_return


    def _add_course(self, weekly_slots, course):
        """Add a course to an schedule"""
        max_hours_per_week = self.constraints['time']['maximum_weekly_effort']
        earliest_start = last_week_for_courses(weekly_slots,
                                               [])#course['prerequisites'])
        if course["duration_code"] == "S":
            t = int(course["duration"]/(60*60))
            t = t if t > 0 else 1
            to_allocate = schedule_hours(t,
                                         weekly_slots,
                                         max_hours_per_week,
                                         earliest_start)
            if to_allocate == None:
                return weekly_slots
            for week, weekly_duration in enumerate(to_allocate):
                if weekly_duration > 0:
                    weekly_slots[week].extend([course]*weekly_duration)
        elif course["duration_code"] == "W":
            # May need to refactor to look for a continuous block of weeks
            weekly_effort = course.get("weekly_effort", 1)
            start_week = schedule_weekly_course(course['duration'],
                                                weekly_effort,
                                                weekly_slots,
                                                max_hours_per_week,
                                                earliest_start)
            if start_week == None:
                # Course does not fit in schedule
                #
                # Changed during add_course method development
                # Will support returning incomplete schedule if too large
                # a skill gap / courses too long
                return weekly_slots
            for i in range(course["duration"]):
                weekly_slots[start_week+i].extend([course]*weekly_effort)
        else:
            weekly_slots[0].extend([course])
        return weekly_slots



def last_week_for_courses(weekly_slots, course_ids):
    """Find the final week for any courses in course_ids

    This is used when a course has prerequisites. The course is only
    scheduled during the final week of the prerequisite courses"""
    last = 0
    for i, week in enumerate(weekly_slots):
        week_ids = [c['id'] for c in week]
        for course_id in course_ids:
            if course_id in week_ids:
                last = i
    return last


def schedule_weekly_course(duration, weekly_effort, weekly_slots,
                           max_hours_per_week, earliest_start=0):
    for i in range(earliest_start,len(weekly_slots)-duration+1):
        fits = True
        for j in range(duration):
            if (len(weekly_slots[i+j]) + weekly_effort) > max_hours_per_week:
                fits = False
        if fits:
            return i
    return None


def schedule_hours(duration, weekly_slots,
                   max_hours_per_week, earliest_start=0):
    for i in range(earliest_start, len(weekly_slots)):
        fits = True
        to_allocate = [0]*len(weekly_slots)
        remaining_duration = duration
        for j in range(len(weekly_slots)-i):
            available = max_hours_per_week - len(weekly_slots[i+j])
            if (sum(to_allocate) > 0) and not available:
                # Course is partly scheduled but now would have to miss a week
                break
            if available > 0:
                weekly_allocation = remaining_duration if remaining_duration < available else available
                to_allocate[i+j] = weekly_allocation
                remaining_duration -= weekly_allocation
            if remaining_duration == 0:
                return to_allocate
    return None


