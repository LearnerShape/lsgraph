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


from flask import abort, Flask, jsonify, request
from pdb import set_trace
import os
import sys
from datetime import datetime
from dateutil.parser import parse
from copy import deepcopy
import pytz
import psycopg2 as pg
from lsengine.graph import *
from lsengine.learner_shape_service import LearnerShapeService
from lsengine.pathway_service import (PathwayService,
                                      normalize_schedule,
                                      normalize_datetime)
from lsengine.job_recommendation import JobRecommendation
from lsengine.workforce_planner import WorkforcePlanner
from lsengine.ls_helpers import *
from werkzeug.exceptions import default_exceptions, HTTPException


#Set up app

with open('config/greeting.txt') as f:
  print(f.read())

app = Flask(__name__)
application = app

phase = os.environ["PHASE"]
if phase is None:
  raise Exception('Unknown phase!')

if phase == 'development':
  db_url = os.getenv("LS_DB_URL_LOCAL")
else:
  db_url = os.getenv("LS_DB_URL")
print('phase ')
print(phase)

print('Start')


@app.before_request
def before_request_func():
  if request.path == '/test':
    return
  if request.path == '/':
    return
  D = request.json
  api_auth = os.environ["ENABLE_API_AUTH"].lower() == 'true'
  PUBLIC_KEY = os.environ.get("API_PUBLIC_KEY", None)
  SECRET_KEY = os.environ.get("API_PRIVATE_KEY", None)
  if not api_auth:
    return
  if (D == None) or ('PUBLIC_KEY' not in D) or ('SECRET_KEY' not in D):
    abort(403)
  if PUBLIC_KEY != D['PUBLIC_KEY']:
    abort(403)
  if SECRET_KEY != D['SECRET_KEY']:
    abort(403)

def load_graphs(G):
  conn = pg.connect(db_url)
  cur = conn.cursor()


  cur.execute('SELECT root_id, graph_tag FROM graphs')
  ids = cur.fetchall()
  for root_id, tag in ids:
    graph = Graph()
    graph.root_id = root_id
    graph.load_data_restricted(db_url, 0, tag)
    G.add(tag, graph)
  conn.close()

class G:
  g = {}

  @classmethod
  def add(cls, identifier, graph):
    cls.g[identifier] = graph

  @classmethod
  def get(cls, D):
    if 'graph_tag' in D:
      identifier = D['graph_tag']
    else:
      identifier = 'ls'
    selected_graph = cls.g[identifier]
 
    return selected_graph

  @classmethod
  def get_all(cls):
    return cls.g.values()


# Add graphs


load_graphs(G)



print('Ready.')





def format_skills(skills, fill='beginner', current=[]):
  """Convert skills to a dictionary structure"""
  if isinstance(skills, list):
    out = {i:fill for i in skills if i not in current}
  else:
    out = {int(i):j for i,j in skills.items()}
  return out


def get_constraints(D):
  if ('constraints' not in D) or not isinstance(D['constraints'], dict):
    return {}
  return D['constraints']


def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    msg = default_exceptions[code].description
    return jsonify({"status_code":code,
                    "status_message":msg}), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


from admin_views import admin
app.register_blueprint(admin, url_prefix='/api/v1')


@app.route('/')
def hello_world():
  """Says hello"""
  return 'Hello, World!'


@app.route('/reload', methods=['GET','POST'])
def reload():
  D = request.json

  # if D and 'graph_tag' in D:
  #   G.get(D).load_data(db_url)
  # else:
  #   for g in G.get_all():
  #     g.load_data(db_url)

  load_graphs(G)
  return jsonify({'status': 'OK'})


@app.route('/test')
def test():
  """Does a small test for the web service test page"""
  g = G.get({})
  k = list(g.skills.keys())[0]
  s = g.skills[k]
  return jsonify(s)


@app.route('/course_alternatives', methods=['POST'])
def course_alternatives():
  """Provide alternative courses teaching a skill.

  Recent issues that should be addressed:
  - providing alternatives for courses that have already bee
  replaced (i.e. the course being replaced may not be the top
  course for a skill)
  - alternatives that are already on the calender teaching
  another skill

  Input: {"schedule":As returned from /schedule,
          "course":ID of the course to change,
          "constraints":Standard format}
  Output: {"courses:[List of courses],
           "status_code":200 on success,
           "status_message":OK on success}"""
  D = request.json

  schedule = D['schedule']
  schedule = normalize_schedule(D['schedule'])
  course_id = D['course']
  constraints = get_constraints(D)

  n_courses = D.get('n_courses', 10)

  PS = PathwayService(G.get(D), [], [], constraints)
  to_return = PS.alternative_courses_for_skills(schedule,
                                                course_id,
                                                n_courses=n_courses)
  to_return['status_code'] = 200
  to_return['status_message'] = 'OK'

  return jsonify(to_return)


@app.route('/courses_for_skill', methods=['POST'])
def courses_for_skill():
  """Course suggestions for a skill.

  This would be called when clicking on a node in the graph

  Input: {"skills":Dictionary of skill id (key) and level (value),
         "constraints":Standard format}
  Output: {"courses":[List of courses],
           "status_code":200 on success,
           "status_message":OK on success}
  """
  D = request.json
  skills = format_skills(D['skills'], 'expert')
  constraints = get_constraints(D)
  n_courses = D.get('n_courses', 10)
  n_courses_per_skill = D.get('n_courses_per_skill', 10)
  user = D.get('user_id', None)

  PS = PathwayService(G.get(D), [], [], constraints)
  to_return = PS.courses_for_skill(skills, user=user,
                                   n_courses=n_courses,
                                   n_courses_per_skill=n_courses_per_skill)
  to_return['status_code'] = 200
  to_return['status_message'] = 'OK'
  return jsonify(to_return)


@app.route('/schedule', methods=['POST'])
def schedule():
  """Return a schedule for a learner.

  This would be called when a schedule does not already exist for a learner.

  Input:  {"current_skills":Dictionary of skill id (key) and level (value),
           "target_skills":Dictionary of skill id (key) and level (value),
           "constraints":Standard format,
           "graph_tag":The graph to use}
  Output: {"schedule":{course_id:{Format as currently returned,
                                  including recent changes, i.e.
                                      "start":isoformat datetime,
                                      "end":isoformat datetime,
                                      "skills":{}},
                       ...
                      }
           "schedule_start":Date of first scheduled course,
           "schedule_end":Date when all courses finish,
           "valid":True|False, whether constraints are satisfied,
           "valid_msg":Details on any constraint violations,
           "status_code":200 on success,
           "status_message":OK on success}
  """
  D = request.json
  c_sk = D['current_skills']
  t_sk = D['target_skills']

  current_skills = format_skills(c_sk, 'beginner')
  target_skills = format_skills(t_sk, 'expert',c_sk)

  constraints = get_constraints(D)

  if 'start' not in D:
    start = datetime.now(tz=pytz.utc)
  else:
    start = normalize_datetime(D['start'])

  graph_of_interest = G.get(D)

  if graph_of_interest.root_id in target_skills:
    target_skills.remove(graph_of_interest.root_id)

  if graph_of_interest.root_id in current_skills:
    current_skills.remove(graph_of_interest.root_id)


  PS = PathwayService(graph_of_interest,
                      current_skills,
                      target_skills,
                      constraints)
  PS.identify_skill_gap()
  PS.get_skill_scores()
  to_return = PS.get_best_schedule(schedule_start=start)
  to_return.update({'status_code':200,
                    'status_message':'OK'})
  return jsonify(to_return)


@app.route('/graph', methods=['POST'])
def ls_graph():
  """Return a graph of the learners current and target skills

  Input: {"current_skills":[List of current skill IDs],
          "target_skills":[List of target skill IDs],
          "mode":dag|graph}
  Output: {"graph":{"nodes":..., "links":...},
           "status_code":200 on success,
           "status_message":OK on success}
  """
  D = request.json
  conn = pg.connect(db_url)
  LSS = LearnerShapeService(G.get(D), conn)
  current_skills = D['current_skills']
  target_skills = D['target_skills']
  method = D['mode']
  result_graph = LSS.call(current_skills, target_skills, method)
  return jsonify({'graph':result_graph,
                  'status_code':200,
                  'status_message':'OK'})


@app.route('/get_member_shape', methods=['POST'])
def get_member_shape():
  D = request.json

  source_ids = D['source_ids']
  target_ids = D['target_ids']

  conn = pg.connect(db_url)
  cursor =conn.cursor()

  LSS = LearnerShapeService(G.get(D), conn)

  result_graph = LSS.call(source_ids,target_ids,'graph')

  return jsonify({'graph':result_graph,
                  'status_code':200,
                  'status_message':'OK'})


@app.route('/get_learnershape', methods=['POST'])
def get_learnershape():
  """Gets a learner shape (to and fom skills graph with nodes and edges)"""
  D = request.json

  p1 = int(D['p1'])
  p2 = D['p2']

  if p2 is not None:
    p2 = int(p2)

  user_id = int(D['user_id'])

  if 'focus_toggle' in D:
    focus_toggle = D['focus_toggle']
  else:
    focus_toggle = False

  if 'hide_source' in D:
    hide_source = D['hide_source']
  else:
    hide_source = False

  # set_trace()

  user_id = int(D['user_id'])
  method = D['method']

  conn = pg.connect(db_url)

  new_graph = G.get(D)

  LSS = LearnerShapeService(new_graph, conn)

  cursor =conn.cursor()

  if focus_toggle:
    ids1 = profile_skill_ids_focussed(cursor,user_id)
    ids2 = profile_skill_ids_focussed(cursor,user_id)
  else:
    ids1 = profile_skill_ids(cursor,p1)
    ids2 = profile_skill_ids(cursor,p2)

    if hide_source:
      ids1 = []
  # Take out the non-focussed skills here


  result_graph = LSS.call(ids1,ids2,method)
  conn.close()

  return jsonify({'graph':result_graph,
                  'status_code':200,
                  'status_message':'OK'})


@app.route('/query', methods=['GET', 'POST'])
def query():
  D = request.json
  return jsonify(G.get(D).full_list())


@app.route('/job/recommendation', methods=['POST'])
def job_recommendation():
  """Compute the suitability of various target profiles for reskilling

  Input:  {"source_profile":ID of a source profile,
           "target_profiles":List of target profile IDs,
           "method":distance|duration,
           "graph_tag":The graph to use (optional, default is ls)}
  Output:  {"profiles":Dict with target profile IDs as keys and
                       values containing:
                       {"distance":Numerical distance to target,
                        "skills":List of {"id":...,
                                          "name":...,
                                          "current_level":...,
                                          "target_level":...}
                                },
            "status_code":200 on success,
            "status_message":OK on success}"""
  D = request.json

  source_profile = D['source_profile']
  target_profiles = D['target_profiles']
  method = D['method']

  conn = pg.connect(db_url)
  cursor =conn.cursor()
  source_skills = profile_skill_levels(cursor,source_profile)
  target_skills = [profile_skill_levels(cursor,i) for i in target_profiles]
  conn.close()

  job_rec = JobRecommendation(G.get(D), db_url)
  if method == 'distance':
    results = job_rec.multiple_jobs_by_distance(source_skills, target_skills)
  elif method == 'duration':
    results = job_rec.multiple_jobs_by_duration(source_skills, target_skills)
  else:
    raise Exception('Method not recognised')

  results = {k:v for k,v in zip(target_profiles, results)}

  return jsonify({'profiles':results,
                  'status_code':200,
                  'status_message':'OK'})


@app.route('/workforce_planning', methods=['POST'])
def workforce_planning():
  """Compute the optimal reskilling actions across a workforce

  Input:  {"organisation_id":ID of an organisation with all employees
                              included in planning,
           "employee_ids":List of employee/user IDs - available
                               as an optional alternative to
                               organisation_id,
           "target_profiles":List of target profiles including number
                               needed and maximum training
                               {'profile_id':...,
                                'number_needed':...,
                                'max_training':...},
           "graph_tag":The graph to use (optional, default is ls)}
  Output:  {"employees_by_target":Dict with target profile IDs as keys and
                       values containing pairs of employee ID
                       and distance,
            "targets_by_employee":Dict with employee/user IDs as keys and
                       values containing pairs of target profile ID
                       and distance,
            "status_code":200 on success,
            "status_message":OK on success}"""
  D = request.json
  conn = pg.connect(db_url)
  cursor =conn.cursor()
  if 'organisation_id' in D:
    # First fetch organisation employee profiles
    employee_profiles = organisation_employee_profiles(cursor,
                                                       D['organisation_id'])
  elif 'employee_ids' in D:
    employee_profiles = get_employee_profiles(cursor, D['employee_ids'])
  else:
    raise Exception('Invalid parameters - either organisation_id or employee_ids must be supplied')

  employee_profiles = profile_skill_levels_batch(cursor, employee_profiles)
  target_profiles = D['target_profiles']
  target_skills = profile_skill_levels_batch(cursor,
                                [i['profile_id'] for i in target_profiles])

  job_rec = JobRecommendation(G.get(D), db_url)
  wp = WorkforcePlanner(job_rec, targets_per_employee=len(target_profiles))
  for k,v in employee_profiles.items():
    wp.add_employee(k, v)

  for tp in target_profiles:
    p_id = tp['profile_id']
    wp.add_target(p_id, target_skills[p_id],
                  tp['number_needed'], tp['max_training'])

  results = wp.plan()
  results.update({'status_code':200,
                  'status_message':'OK'})
  return jsonify(results)

