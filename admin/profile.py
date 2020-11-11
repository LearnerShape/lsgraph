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

from datetime import datetime
from flask import abort

from application import app


def get_profiles(db_conn, organisation_id):
    q = "SELECT id,name FROM profiles"
    if organisation_id:
        q = """SELECT profiles.id,profiles.name FROM profiles
        RIGHT JOIN organisations
        ON profiles.graph = organisations.graph
        WHERE organisations.id = %s AND user_id IS NULL"""
    cursor = db_conn.cursor()
    cursor.execute(q, [organisation_id, ])
    output = [{"id":profile_id,
               "name":profile_name} for profile_id,profile_name in cursor.fetchall()]
    return output


def create_profile(db_conn, organisation_id, data):
    cursor = db_conn.cursor()
    cursor.execute("SELECT graph FROM organisations WHERE id = %s",
                   [organisation_id,])
    org_graph = cursor.fetchone()[0]
    q = """INSERT INTO profiles
    (name, graph)
    VALUES (%(name)s, %(graph)s)
    RETURNING id"""
    params = {"name":data["name"],
              "graph":org_graph}
    cursor.execute(q, params)
    profile_id = cursor.fetchone()[0]
    q = """INSERT INTO competences (level, skill_id, profile_id)
    VALUES (%(level)s, %(skill_id)s, %(profile_id)s)"""
    for skill_id,level in data["competences"].items():
        cursor.execute(q, {"skill_id":int(skill_id),
                           "level":level,
                           "profile_id":profile_id})
    db_conn.commit()
    return {"id":profile_id}


def get_profile_detail(db_conn, profile_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id,name FROM profiles WHERE id = %s",
                   [user_id,])
    profile_detail = cursor.fetchone()
    profile_detail = {k.name:v for k,v in zip(cursor.description, profile_detail)}
    # Get competences
    cursor.execute("""SELECT skill_id,level FROM competences
    WHERE profile_id = %s""", [profile_id,])
    competences = {skill_id:level for skill_id,level in cursor.fetchall()}
    profile_detail["competences"] = competences
    return profile_detail
