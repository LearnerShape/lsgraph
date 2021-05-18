from flask.views import MethodView


class ProfilesAPI(MethodView):
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


class ProfilesDetailAPI(MethodView):
    def get(self, org_uuid, profile_uuid):
        """Groups endpoint

        .. :quickref: Get groups

        """
        return "Hello"

    def put(self, org_uuid, profile_uuid):
        """Groups endpoint

        .. :quickref: Create new group

        """
        return "Hello"

    def delete(self, org_uuid, profile_uuid):
        """Groups endpoint

        .. :quickref: Create new group

        """
        return "Hello"
