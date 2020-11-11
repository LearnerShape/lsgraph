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


def get_users(db_conn, organisation_id):
    q = "SELECT id,name FROM users"
    if organisation_id:
        q = """SELECT users.id,users.name FROM users RIGHT JOIN members
        ON users.id = members.user_id WHERE members.organisation_id = %s"""
    cursor = db_conn.cursor()
    cursor.execute(q, [organisation_id, ])
    output = [{"id":user_id,
               "name":user_name} for user_id,user_name in cursor.fetchall()]
    return output


def create_user(db_conn, organisation_id, data):
    cursor = db_conn.cursor()
    cursor.execute("SELECT graph FROM organisations WHERE id = %s",
                   [organisation_id,])
    org_graph = cursor.fetchone()[0]
    q = """INSERT INTO users
    (email, created_at, updated_at, name, default_graph)
    VALUES (%(email)s, %(created_at)s, %(updated_at)s, %(name)s, %(graph)s)
    RETURNING id"""
    params = {"email":data["email"],
              "created_at":datetime.now(),
              "updated_at":datetime.now(),
              "name":data["name"],
              "graph":org_graph}
    cursor.execute(q, params)
    user_id = cursor.fetchone()[0]
    q = """INSERT INTO profiles (user_id, graph)
    VALUES (%(user_id)s, %(graph)s) RETURNING id"""
    cursor.execute(q, {"user_id":user_id,
                       "graph":org_graph})
    profile_id = cursor.fetchone()[0]
    q = """INSERT INTO competences (level, skill_id, profile_id)
    VALUES (%(level)s, %(skill_id)s, %(profile_id)s)"""
    for skill_id,level in data["competences"].items():
        cursor.execute(q, {"skill_id":int(skill_id),
                           "level":level,
                           "profile_id":profile_id})
    q = """INSERT INTO members (created_at, updated_at,
    user_id, organisation_id)
    VALUES (%(created_at)s, %(updated_at)s,
    %(user_id)s, %(organisation_id)s)"""
    cursor.execute(q, {"created_at":datetime.now(),
                       "updated_at":datetime.now(),
                       "user_id":user_id,
                       "organisation_id":organisation_id})
    db_conn.commit()
    return {"id":user_id}


def get_user_detail(db_conn, user_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id,email,name,default_graph,created_at,updated_at FROM users WHERE id = %s",
                   [user_id,])
    org_detail = cursor.fetchone()
    org_detail = {k.name:v for k,v in zip(cursor.description, org_detail)}
    return org_detail
