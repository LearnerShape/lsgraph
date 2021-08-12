# Copyright (C) 2021  Learnershape and contributors

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


import os

from flask import Flask
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("lsgraph.config")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    if app.config["ENV"] == "production":
        assert app.config["SECRET_KEY"] != "DEVELOPMENT", "Secret key must be changed"

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import models

    models.db.init_app(app)
    migrate = Migrate(app, models.db)

    api = Api(
        app,
        spec_kwargs={
            "security": [{"APIKey": [], "AuthToken": []}],
            "servers": [
                {
                    "url": "https://www.learnershape.com",
                    "description": "Learnershape hosted service",
                }
            ],
        },
    )

    api.spec.components.security_scheme(
        "APIKey", {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    )
    api.spec.components.security_scheme(
        "AuthToken", {"type": "apiKey", "in": "header", "name": "X-Auth-Token"}
    )

    from . import api_v1

    api.register_blueprint(api_v1.api)

    return app
