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

import hashlib
import secrets
import string


class AccessKey:
    def __init__(self, secret_key):
        """Access/secret key handling"""
        self.options = string.digits + string.ascii_lowercase + string.ascii_uppercase
        self.secret_key = secret_key

    def generate_pair(self):
        """Create a new pair of keys"""
        access_id = "LS" + "".join(secrets.choice(self.options) for i in range(18))
        access_secret = "".join(secrets.choice(self.options) for i in range(38))
        check_text = self.secret_key + access_id + access_secret
        check = hashlib.sha512(check_text.encode("ascii")).hexdigest()[:2]
        access_secret += check
        return access_id, access_secret

    def validate_pair(self, access_id, access_secret):
        """Verify that key pair is well-formed"""
        check_text = self.secret_key + access_id + access_secret[:-2]
        check = access_secret[-2:]
        return check == hashlib.sha512(check_text.encode("ascii")).hexdigest()[:2]
