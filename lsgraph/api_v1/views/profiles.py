from flask.views import MethodView


class ProfilesAPI(MethodView):
    def get(self, org_uuid):
        """Profiles endpoint

        .. :quickref: Get profiles

        """
        return "Hello"

    def post(self, org_uuid):
        """Profile creation endpoint

        .. :quickref: Create new profile

        """
        return "Hello"


class ProfilesDetailAPI(MethodView):
    def get(self, org_uuid, profile_uuid):
        """Profile detail endpoint

        .. :quickref: Get profile detail

        """
        return "Hello"

    def put(self, org_uuid, profile_uuid):
        """Profile update endpoint

        .. :quickref: Update profile

        """
        return "Hello"

    def delete(self, org_uuid, profile_uuid):
        """Profile deletion endpoint

        .. :quickref: Delete profile

        """
        return "Hello"
