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


from lsgraph.utils.access_key import AccessKey


def test_generate_pair():
    ak = AccessKey("secret")
    access_id, access_secret = ak.generate_pair()
    assert access_id.startswith("LS")
    assert len(access_id) == 20
    assert len(access_secret) == 40
    assert ak.validate_pair(access_id, access_secret)


def test_validate_pair():
    ak = AccessKey("secret")
    access_id, access_secret = ak.generate_pair()
    assert ak.validate_pair(access_id, access_secret)
    ak2 = AccessKey("secret2")
    assert not ak2.validate_pair(access_id, access_secret)
