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


class OrganizationsAPI(MethodView):
    def get(self):
        """Organizations endpoint

        .. :quickref: Get organizations

        """
        return "Hello"

    def post(self):
        """Organization creation endpoint

        .. :quickref: Create new organization

        """
        return "Hello"


class OrganizationsDetailAPI(MethodView):
    def get(self, org_uuid):
        """Organization detail endpoint

        .. :quickref: Get organization detail

        """
        return "Hello"

    def put(self, org_uuid):
        """Organization update endpoint

        .. :quickref: Update organization

        """
        return "Hello"

    def delete(self, org_uuid):
        """Organization deletion endpoint

        .. :quickref: Delete organization

        """
        return "Hello"
