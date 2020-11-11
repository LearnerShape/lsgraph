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

from collections import defaultdict
from datetime import datetime
from flask import abort

from application import app

def get_graphs(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id,name,graph_tag FROM graphs")
    output = [{'id':i[0],
               'name':i[1],
               'graph_tag':i[2]} for i in cursor.fetchall()]
    return output


def create_new_root(cursor, graph_tag):
    q = """INSERT INTO skills (name, created_at, modified_at, graph)
    VALUES (%(name)s, %(created_at)s, %(modified_at)s, %(graph_tag)s)
    RETURNING id"""
    params = {"name":"Root",
              "created_at":datetime.now(),
              "modified_at":datetime.now(),
              "graph_tag":graph_tag}
    cursor.execute(q, params)
    root_id = cursor.fetchone()
    return root_id


def add_skills_to_graph(cursor, parent_id, graph, graph_tag):
    new_skill_q = """INSERT INTO skills (name, created_at, modified_at,
    graph) VALUES (%(name)s, %(created_at)s, %(modified_at)s, %(graph_tag)s)
    RETURNING id"""
    new_link_q = """INSERT INTO skill_includes (subject_id, object_id,
    created_at, modified_at)
    VALUES(%(subject_id)s, %(object_id)s, %(created_at)s, %(modified_at)s)"""
    for k,v in graph.items():
        if k == '_meta':
            continue
        cursor.execute(new_skill_q, {"name":k,
                                     "created_at":datetime.now(),
                                     "modified_at":datetime.now(),
                                     "graph_tag":graph_tag})
        object_id = cursor.fetchone()
        cursor.execute(new_link_q, {"subject_id":parent_id,
                                    "object_id":object_id,
                                    "created_at":datetime.now(),
                                    "modified_at":datetime.now()})
        add_skills_to_graph(cursor, object_id, v, graph_tag)


def create_graph(db_conn, data):
    """Create a new graph"""
    cursor = db_conn.cursor()
    # Check that graph_tag is unique
    graph_tag = data["graph_tag"]
    cursor.execute("""SELECT COUNT(*) FROM graphs WHERE graph_tag = %s""",
                   [graph_tag, ])
    existing_graph = cursor.fetchone()
    if existing_graph != (0,):
        app.logger.error('Graph already exists {0}'.format(existing_graph))
        abort(500)
    # Create new root skill
    root_id = create_new_root(cursor, graph_tag)
    # Iteratively add skills and links
    add_skills_to_graph(cursor, root_id, data["graph"], graph_tag)
    # Create graph record
    new_graph_q = """INSERT INTO graphs (created_at, updated_at, graph_tag,
    name, description, root_id) VALUES (%(created_at)s, %(updated_at)s,
    %(graph_tag)s, %(name)s, %(description)s, %(root_id)s) RETURNING id"""
    new_graph_params = {"created_at":datetime.now(),
                        "updated_at":datetime.now(),
                        "graph_tag":graph_tag,
                        "name":data["name"],
                        "description":data["description"],
                        "root_id":root_id}
    cursor.execute(new_graph_q, new_graph_params)
    new_id = cursor.fetchone()[0]
    db_conn.commit()
    # TODO Run cacher

    return {"id":new_id}


def get_graph_detail(db_conn, graph_id):
    """Fetch details information on a graph"""
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM graphs WHERE id = %s", [graph_id, ])
    graph_info = cursor.fetchone()
    graph_info = {k.name:v for k,v in zip(cursor.description, graph_info)}
    # Get skills graph
    cursor.execute("SELECT id,name FROM skills WHERE graph = %s",
                   [graph_info["graph_tag"], ])
    skills = cursor.fetchall()
    skills = {skill_id:skill_name for skill_id,skill_name in skills}
    q = "SELECT subject_id,object_id FROM skill_includes"
    cursor.execute(q, )
    skill_includes = defaultdict(list)
    for subject_id,object_id in cursor.fetchall():
        skill_includes[subject_id].append(object_id)
    graph = {}
    def build_graph(graph, current_id):
        for i in skill_includes[current_id]:
            graph[skills[i]] = {"_meta":{"id":i}}
            build_graph(graph[skills[i]], i)
    build_graph(graph, graph_info["root_id"])
    graph_info["graph"] = graph
    return graph_info






