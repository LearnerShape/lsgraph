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

from bs4 import BeautifulSoup
import numpy as np
from sqlalchemy.dialects import postgresql
import time

def collect(names):
  result = {}
  for var in names:
    result[var] = eval(var)
  return R

def pp_skills(D):
  #Prints list of dicts
  for x in D:
    print(f"{x['name']} ({x['id']}")


def clean(x):
  if x is None:
    return ''
  soup = BeautifulSoup(x, 'lxml')
  text = soup.get_text()
  text = text.replace('\n',' ')
  return text

def isnan(x):
  if type(x) == type('s'):
    return False
  if np.isnan(x):
    return True


def actual_query(q):
  st = q.statement
  return st.compile(dialect=postgresql.dialect(),
                                 compile_kwargs={'literal_binds': True})
def t0():
  return time.time()

def t1(_t0):

  _t1 = time.time()
  print('finish '+str(round(_t1-_t0,3)))
