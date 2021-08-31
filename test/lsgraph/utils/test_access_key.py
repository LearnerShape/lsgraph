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
