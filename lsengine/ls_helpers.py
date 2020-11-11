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


def get_ids(cur,q):
  cur.execute(q)
  res = []
  for row in cur.fetchall():
    res.append(row[0])
  return res


def profile_skill_ids(cursor,p):
  q = """SELECT skill_id FROM competences INNER JOIN skills ON competences.skill_id = skills.id WHERE profile_id=%s"""
  cursor.execute(q, [p])
  results = [i[0] for i in cursor.fetchall()]
  return results


def profile_skill_ids_focussed(cursor,p):
  q = f"""SELECT user_id FROM profiles WHERE id = {p}"""
  cursor.execute(q)
  user_id = get_ids(cursor,q)[0]

  q = f"""SELECT competences.skill_id FROM 
  competences INNER JOIN skills 
  ON competences.skill_id = skills.id
  INNER JOIN focused_skills
  ON skills.id = focused_skills.skill_id
  WHERE focused_skills.user_id = {user_id}
"""
  return get_ids(cursor,q)

def profile_skill_levels(cursor,p):
  """Return profile as skill_id:level dictionary"""
  q = """SELECT skill_id, level FROM competences INNER JOIN skills ON competences.skill_id = skills.id WHERE profile_id=%s"""
  cursor.execute(q, [p])
  results = {skill_id:level for skill_id,level in cursor.fetchall()}
  return results


def profile_skill_levels_batch(cursor, profile_ids):
  """Load multiple profiles as skill_id:level dictionaries"""
  if len(profile_ids) == 0:
    return {}
  q = """SELECT profile_id, skill_id, level FROM competences INNER JOIN skills ON competences.skill_id = skills.id WHERE profile_id = ANY(%s)"""
  if isinstance(profile_ids[0], int):
    output = {k:{} for k in profile_ids}
    p_id = profile_ids
    m = {i:i for i in profile_ids}
  elif isinstance(profile_ids[0], dict):
    output = {k["user_id"]:{} for k in profile_ids}
    p_id = [i['profile_id'] for i in profile_ids]
    m = {i["profile_id"]:i["user_id"] for i in profile_ids}
  cursor.execute(q, [p_id])
  results = cursor.fetchall()
  for p,s,l in results:
    output[m[p]][s] = l
  return output


def organisation_employee_profiles(cursor, organisation_id):
  """Fetch all employee profile IDs for an organisation"""
  q = """SELECT profiles.user_id, profiles.id FROM profiles, members WHERE profiles.user_id = members.user_id AND members.organisation_id = %s AND profiles.kind IS NULL"""
  cursor.execute(q, [organisation_id])
  results = [{"user_id":i[0], "profile_id":i[1]} for i in cursor.fetchall()]
  return results


def get_employee_profiles(cursor, employee_ids):
  """Fetch all employee profile IDs for a list of user IDs"""
  q = """SELECT profiles.user_id, profiles.id FROM profiles WHERE profiles.user_id = ANY(%s) AND profiles.kind IS NULL"""
  cursor.execute(q, [employee_ids])
  results = [{"user_id":i[0], "profile_id":i[1]} for i in cursor.fetchall()]
  return results

