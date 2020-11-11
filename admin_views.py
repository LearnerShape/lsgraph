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

from flask import abort, Blueprint, jsonify, request
import psycopg2 as pg

from application import db_url, app
from admin.graph import get_graphs, create_graph, get_graph_detail
from admin.organisation import (get_organisations,
                                create_organisation,
                                get_organisation_detail)
from admin.user import get_users, create_user, get_user_detail
from admin.profile import get_profiles, create_profile, get_profile_detail

admin = Blueprint('admin', __name__)

db_conn = pg.connect(db_url)



@admin.route('/')
def index():
    return "Hello"


@admin.route('/graphs', methods=['GET', 'POST',])
def graphs():
    """List and create graphs"""
    if request.method == 'GET':
        all_graphs = get_graphs(db_conn)
        return jsonify(all_graphs)
    new_graph = create_graph(db_conn, request.json)
    return jsonify(new_graph)


@admin.route('/graphs/<int:graph_id>', methods=['GET',])
def graph_detail(graph_id):
    """Get detailed information on a graph"""
    graph = get_graph_detail(db_conn, graph_id)
    return jsonify(graph)


@admin.route('/organisations', methods=['GET', 'POST',])
def organisations():
    """List and create organisations"""
    if request.method == "GET":
        all_organisations = get_organisations(db_conn)
        return jsonify(all_organisations)
    new_organisation = create_organisation(db_conn, request.json)
    return jsonify(new_organisation)


@admin.route('/organisations/<int:organisation_id>', methods=['GET',])
def organisation_detail(organisation_id):
    """Get detailed information on an organisation"""
    organisation = get_organisation_detail(db_conn, organisation_id)
    return jsonify(organisation)


@admin.route('/users', methods=['GET', 'POST',],
             defaults={'organisation_id':None})
@admin.route('organisations/<int:organisation_id>/users',
             methods=['GET', 'POST',])
def users(organisation_id):
    """List and create users"""
    if request.method == "GET":
        all_users = get_users(db_conn, organisation_id)
        return jsonify(all_users)
    if not organisation_id:
        return "Users must be created within an organisation", 501
    new_user = create_user(db_conn, organisation_id, request.json)
    return jsonify(new_user)


@admin.route('/users/<user_id>', methods=['GET',],
             defaults={'organisation_id':None})
@admin.route('/organisations/<int:organisation_id>/users/<int:user_id>',
             methods=['GET',])
def user_detail(organisation_id, user_id):
    """Get detailed information on a user"""
    user = get_user_detail(db_conn, user_id)
    return jsonify(user)


@admin.route('/profiles', methods=['GET', 'POST',],
             defaults={'organisation_id':None})
@admin.route('/organisations/<int:organisation_id>/profiles',
             methods=['GET', 'POST',])
def profiles(organisation_id):
    """List and create profiles"""
    if request.method == "GET":
        all_profiles = get_profiles(db_conn, organisation_id)
        return jsonify(all_profiles)
    if not organisation_id:
        return "Profiles must be created within an organisation", 501
    new_profile = create_profile(db_conn, organisation_id, request.json)
    return jsonify(new_profile)


@admin.route('/profiles/<profile_id>', methods=['GET',],
             defaults={'organisation_id':None})
@admin.route('/organisations/<int:organisation_id>/profiles/<int:profile_id>',
             methods=['GET',])
def profile_detail(organisation_id, profile_id):
    """Get detailed information on a profile"""
    profile = get_profile_detail(db_conn, profile_id)
    return jsonify(profile)






