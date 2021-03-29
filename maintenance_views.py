from flask import Blueprint, jsonify, request
import psycopg2 as pg

maintenance = Blueprint('maintenance', __name__)

from application import db_url, app, G, load_graphs
from lsengine.cacher import Cacher
from lsengine.graph import Graph

@maintenance.route('/refresh_cache')
def refresh_cache():
    conn = pg.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT root_id,graph_tag FROM graphs")
    graphs = cursor.fetchall()
    conn.close()
    for root_id, graph_tag in graphs:
        g = Graph()
        g.root_id = root_id
        g.load_data_restricted(db_url, graph=graph_tag)
        c = Cacher(db_url)
        c.cache_paths_and_depths(g, root_id, graph_tag)
    # Regenerate the local cache
    load_graphs(G)
    return jsonify({'status_code':200,
                    'status_message':'OK'})
