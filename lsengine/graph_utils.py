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

# Various utilities for manipulating lists of nodes and edges

def findid(l,x):
  for r in l:
    if r['id'] == x:
      return r
    
def get_node(n,x):
  for p in n:
    if p['id'] == x:
      return p
  return None
    
def find_parent(ls,g):
  for l in ls:
    if l['target'] == g:
      return l['source']
  return None
  
def merge_trees(n1,l1,n2,l2):
  #print('---------------','MERGE')
  for n in n1:
    n['group'] = 1
    n['source'] = True
    n['target'] = False
    n['both'] = False
  for n in n2:
    #print('---------------',n)
    n['group'] = 2
    n['target'] = True
    n['source'] = False
    n['both'] = False
    if not findid(n1, n['id']):
      #print('not in!')
      n1.append(n)
      npi = find_parent(l2,n['id'])
      l1.append({'source':npi,'target':n['id']})
      #print('append', n)
      #print(npi,n['id'])
      go = True
      while go:
        if not findid(n1, npi):
          n_new = get_node(n2,npi)
          n1.append(n_new)
          #print('append', n_new)
          l1.append({'source':npi,'target':n['id']})
          #print(npi,n['id'])
          npi = find_parent(l2,npi)
          n = n_new
          if npi is None:
            go = False
        else:
          l1.append({'source':npi,'target':n['id']})
          go = False
    else:
      #print('already in!')
      node_already_in = findid(n1, n['id'])
      node_already_in['both'] = True
  return {'nodes':n1, 'links':l1}

def children(l,n):
  out = []
  for e in l:
    if e['source'] == b:
      out=append(s['target'])
  return out

def tree_search(t,x):
  return tree_search_r(n,x)

def tree_search_r(n,x):
  if n['id'] == x:
    return n
  else:
    for c in children(t):
      r = tree_search_r(c,x)
      if r is not None:
        return r
    return None
    
