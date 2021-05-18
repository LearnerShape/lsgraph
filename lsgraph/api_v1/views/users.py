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


class UsersAPI(MethodView):
    def get(self, org_uuid):
        """Users endpoint

        .. :quickref: Get users

        """
        return "Hello"

    def post(self, org_uuid):
        """User creation endpoint

        .. :quickref: Create new user

        """
        return "Hello"


class UsersDetailAPI(MethodView):
    def get(self, org_uuid, user_uuid):
        """User detail endpoint

        .. :quickref: Get user detail

        """
        return "Hello"

    def put(self, org_uuid, user_uuid):
        """User update endpoint

        .. :quickref: Update user

        """
        return "Hello"

    def delete(self, org_uuid, user_uuid):
        """User deletion endpoint

        .. :quickref: Delete user

        """
        return "Hello"
