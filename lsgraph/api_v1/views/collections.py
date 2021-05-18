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


class CollectionsAPI(MethodView):
    def get(self, org_uuid=None):
        """Collections endpoint

        .. :quickref: Get collections

        """
        return "Hello"

    def post(self, org_uuid=None):
        """Collection creation endpoint

        .. :quickref: Create new collection

        """
        return "Hello"


class CollectionsDetailAPI(MethodView):
    def get(self, collection_uuid, org_uuid=None):
        """Collection detail endpoint

        .. :quickref: Get collection detail

        """
        return "Hello"

    def put(self, collection_uuid, org_uuid=None):
        """Collection update endpoint

        .. :quickref: Update collection

        """
        return "Hello"

    def delete(self, collection_uuid, org_uuid=None):
        """Collection deletion endpoint

        .. :quickref: Delete collection

        """
        return "Hello"


class CollectionResourcesAPI(MethodView):
    def get(self, collection_uuid, org_uuid=None):
        """Collection resources endpoint

        .. :quickref: Get collection resources

        """
        return "Hello"

    def put(self, collection_uuid, org_uuid=None):
        """Collection resources update endpoint

        .. :quickref: Update collection resources

        """
        return "Hello"

    def delete(self, collection_uuid, org_uuid=None):
        """Collection resources deletion endpoint

        .. :quickref: Delete collection resources

        """
        return "Hello"
