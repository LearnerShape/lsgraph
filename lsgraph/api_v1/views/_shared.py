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


import pdb
from flask import g
from flask_smorest import abort


def authorized_org(f):
    """Checks whether customer is authorized to operate on organization"""

    def decorator(*args, **kwargs):
        if kwargs["org_uuid"] not in g.organizations:
            pdb.set_trace()
            abort(401)
        return f(*args, **kwargs)

    return decorator
