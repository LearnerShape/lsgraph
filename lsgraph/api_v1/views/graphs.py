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


from flask.views import MethodView


class GraphsAPI(MethodView):
    def get(self):
        """Graphs endpoint

        .. :quickref: Get graphs

        """
        return "Hello"

    def post(self):
        """Graph creation endpoint

        .. :quickref: Create new graph

        """
        return "Hello"


class GraphsDetailAPI(MethodView):
    def get(self, graph_uuid):
        """Graph detail endpoint

        .. :quickref: Get graph detail

        """
        return "Hello"

    def put(self, graph_uuid):
        """Graph update endpoint

        .. :quickref: Update graph

        """
        return "Hello"

    def delete(self, graph_uuid):
        """Graph deletion endpoint

        .. :quickref: Delete graph

        """
        return "Hello"
