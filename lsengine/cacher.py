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


import psycopg2 as pg
import json

from pdb import set_trace

class Cacher:


  def __init__(self, url):
    self.url = url
    self.conn = pg.connect(url)
    self.cur = self.conn.cursor()


  def exec(self,query, params=None):
    if params == None:
      self.cur.execute(query)
      print(query)
    else:
      self.cur.execute(query, params)
      print(self.cur.query)


  def commit(self):
    print('COMMIT')
    self.conn.commit()


  def cache_paths_and_depths_from_roots(self, graph, wipe_all=False):
    self.cur.execute('SELECT root_id, graph_tag FROM graphs')
    ids = self.cur.fetchall()
    print('GRAPH IDS')
    print(ids)
    for id in ids:
      rid = id[0]
      tag = id[1]
      print('Caching ',rid)
      self.cache_paths_and_depths(graph, rid, tag, wipe_all)


  def cache_paths_and_depths(self, graph, root_id, graph_tag, wipe_all=False):
    print('Start')

    #q = 'UPDATE skills SET search_tag=NULL'
    #self.exec(q)

    paths, depths, below = graph.find_paths_and_depth_from_root(root_id) 
    
    print('Loop')
    for k in paths.keys():
      if k == root_id:
        n_below = len(set(below[root_id]))
        q = "UPDATE skills SET path_from_root='[]', depths='[0]', text_path='[]', search_tag='OK', to_delete=FALSE, graph=%(graph_tag)s, n_below=%(n_below)s WHERE id=%(k)s"
        self.exec(q, {'graph_tag':graph_tag,
                      'n_below':n_below,
                      'k':k})
      else:

        if (paths[k] == graph.skills[k]['path_from_root']) and \
              (depths[k] == graph.skills[k]['depth']) and not wipe_all:
          print(k, 'already up to date in db')
          continue

        text_paths = []
        for p in paths[k]:
          tp = [graph.skills[x]['name'] for x in p]
          tp = '/'.join(tp[1:])
          text_paths.append(tp)
        text_paths = json.dumps(text_paths)
        d = json.dumps(depths[k])
        path = json.dumps(paths[k])
        n_below = len(set(below[k]))
        # if 1:
        #   n_below = len(set(below[k])
        # else:
        #   set_trace()
        q = "UPDATE skills SET path_from_root=%(path)s, depths=%(d)s, text_path=%(text_paths)s, search_tag='OK', to_delete=FALSE, graph=%(graph_tag)s, n_below=%(n_below)s WHERE id=%(k)s"
        self.exec(q, {'path':path,
                      'd':d,
                      'text_paths':text_paths,
                      'graph_tag':graph_tag,
                      'n_below':n_below,
                      'k':k})
    self.commit()
