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

import time, os
import numpy as np
import pickle
from pdb import set_trace
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, load_only
from .models import *


class RobustCache:
    """Queries database if item is not found in the cache"""

    def __init__(self, query_func):
        self.query_func = query_func
        self.cache = {}


    def __setitem__(self, key, value):
        self.cache[key] = value


    def __getitem__(self, key):
        if key not in self.cache:
            # Query database for value
            value = self.query_func(key)
            self.cache[key] = value
        return self.cache[key]


    def __contains__(self, key):
        return key in self.cache


    def __len__(self):
        return len(self.cache)


    def keys(self):
        return self.cache.keys()


    def values(self):
        return self.cache.values()



def generic_query_func(session, model, columns):
    """Create a function to query a database table"""
    def specific_query_func(key):
        """Custoimized function to lookup a entry in a specific table"""
        r = session.query(model).filter(model.id == key).one()
        return {c:r.__dict__[c] for c in columns}
    return specific_query_func





class Graph:
  """Cache of graph"""


  def __init__(self, root_id=None):
    if root_id:
      self.root_id = root_id


  def load_data(self, database_url, delay=0):
    """Load all data to process locally and manage db connection"""
    self.engine = create_engine(database_url, echo=True,
      connect_args= { 'connect_timeout': 60 })
    self.Session = sessionmaker()
    self.Session.configure(bind=self.engine)
    session = self.Session()
    try:
        self._load_data(session)
        session.commit()
    except:
        session.rollback()
        print("Error loading data")
        if delay != 0:
            time.sleep(2**delay)
        delay = delay+1 if delay<8 else 8
        self.load_data(database_url, delay)
    finally:
        session.close()


  def load_data_restricted(self, database_url, delay=0, graph='ls'):
    """Load all data to process locally and manage db connection"""
    self.engine = create_engine(database_url, echo=True,
      connect_args= { 'connect_timeout': 60 })
    self.Session = sessionmaker()
    self.Session.configure(bind=self.engine)
    session = self.Session()
    try:
        self._load_data_restricted(session, graph)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error loading data")
        print(e)
        if delay != 0:
            time.sleep(2**delay)
        delay = delay+1 if delay<8 else 8
        self.load_data_restricted(database_url, delay, graph)
    finally:
        session.close()

  def _load_data(self,session):
    """Load all data to process locally"""
    print('begin loading data')

    print('QUERY ----- BEGIN')
    skills = session.query(Skill)
    self.skills = {}
    for s in skills:
      self.skills[s.id] = {'name':s.name,
                             'id':s.id,
                             'depth':s.depth,
                             'path_from_root':s.path_from_root,
                             'description':s.description,
                             'scores':[],}
    print('QUERY ----- END')
    print('QUERY ----- BEGIN')
    includes = session.query(SkillIncludes)
    self.includes = {}
    for i in includes:
        self.includes[i.id] = {'subject_id':i.subject_id,
                               'object_id':i.object_id,
                               'id':i.id}
    print('QUERY ----- END')


  def _load_data_restricted(self,session, graph):
    """Load all data to process locally."""

    # OK to load all skill_includes
    # personal or not, because only the ones
    # 
    print('begin loading data')

    print('QUERY ----- BEGIN')
    skills = session.query(Skill).filter_by(graph=graph, personal=False)
 
    #self.skills = {}
    skill_func = generic_query_func(session, Skill, ['name',
                                                     'id',
                                                     'depth',
                                                     'path_from_root',
                                                     'description'])
    self.skills = RobustCache(query_func = skill_func)
    for s in skills:

      self.skills[s.id] = {'name':s.name,
                             'id':s.id,
                             'depth':s.depth,
                             'path_from_root':s.path_from_root,
                             'description':s.description,
                             'scores':[],}
    print('QUERY ----- END')
    print('QUERY ----- BEGIN')
    # TODO: update this to only query skill_includes belonging to this graph
    includes = session.query(SkillIncludes)
    self.includes = {}
    for i in includes:
        self.includes[i.id] = {'subject_id':i.subject_id,
                               'object_id':i.object_id,
                               'id':i.id}
    print('QUERY ----- END')



  def children(self, id):
    """Helper method to get all children

    Nodes connected by an outgoing edge"""
    children = []
    for i in self.includes.values():
      if i['subject_id'] == id:
        children.append(i['object_id'])
    return children



  paths_dict = {}
  depths_dict = {}
  def find_paths_and_depth_from_root(self,root):
    global paths_dict
    global depths_dict
    global below_dict
    print('CACHING PATHS...')
    paths_dict = {}
    depths_dict = {}
    below_dict = {}
    t1 = time.time()
    self.find_paths_and_depths_from_root_r(root, [], 0)
    t2 = time.time()
    print('DONE', round(t2-t1,3))
    return paths_dict, depths_dict, below_dict


  def find_paths_and_depths_from_root_r(self, id, path, depth):
    """Processing path and depth from root in single pass"""
    # Dict is required as recursing through a DAG, we may return
    # up through each node multiple times

    # below_dict is not deduplicated here!
    global paths_dict
    global depths_dict
    global below_dict
    if id not in paths_dict:
      paths_dict[id] = [path]
    else:
      paths_dict[id] += [path]
    if id not in depths_dict:
      depths_dict[id] = [depth]
    else:
      depths_dict[id] += [depth]
    child_ids = self.children(id)

    if child_ids:
      l_below = []
      for cid in child_ids:
          r_below = self.find_paths_and_depths_from_root_r(cid, path+[id], depth+1)
          l_below += r_below
      if id not in below_dict:
        below_dict[id] = l_below
      else:
        below_dict[id] += l_below
      return l_below + [id]
    else:
      below_dict[id] = []
      return [id]

