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


def get_organisations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id,name FROM organisations")
    output = [{"id":org_id,
               "name":org_name} for org_id,org_name in cursor.fetchall()]
    return output


def create_organisation(db_conn, data):
    cursor = db_conn.cursor()
    q = """INSERT INTO organisations
    (created_at, updated_at, name, graph)
    VALUES (%(created_at)s, %(updated_at)s, %(name)s, %(graph)s)
    RETURNING id"""
    params = {"created_at":datetime.now(),
              "updated_at":datetime.now(),
              "name":data["name"],
              "graph":data["graph"]}
    cursor.execute(q, params)
    org_id = cursor.fetchone()[0]
    db_conn.commit()
    return {"id":org_id}


def get_organisation_detail(db_conn, organisation_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id,name,graph,created_at,updated_at FROM organisations WHERE id = %s",
                   [organisation_id,])
    org_detail = cursor.fetchone()
    org_detail = {k.name:v for k,v in zip(cursor.description, org_detail)}
    return org_detail
