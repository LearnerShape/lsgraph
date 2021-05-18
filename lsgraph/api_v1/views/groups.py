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


class GroupsAPI(MethodView):
    def get(self, org_uuid):
        """Groups endpoint

        .. :quickref: Get groups

        """
        return "Hello"

    def post(self, org_uuid):
        """Groups endpoint

        .. :quickref: Create new group

        """
        return "Hello"


class GroupsDetailAPI(MethodView):
    def get(self, org_uuid, group_uuid):
        """Groups endpoint

        .. :quickref: Get groups

        """
        return "Hello"

    def put(self, org_uuid, group_uuid):
        """Groups endpoint

        .. :quickref: Create new group

        """
        return "Hello"

    def delete(self, org_uuid, group_uuid):
        """Groups endpoint

        .. :quickref: Create new group

        """
        return "Hello"
