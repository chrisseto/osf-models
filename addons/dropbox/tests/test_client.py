from nose.tools import *  # noqa (PEP8 asserts)
import unittest

import pytest

from tests.factories import UserFactory

from website.addons.dropbox.model import DropboxUserSettings


pytestmark = pytest.mark.django_db


class TestCore(unittest.TestCase):

    def setUp(self):

        super(TestCore, self).setUp()

        self.user = UserFactory()
        self.user.add_addon('dropbox')
        self.user.save()

        self.settings = self.user.get_addon('dropbox')
        self.settings.access_token = '12345'
        self.settings.save()

    def test_get_addon_returns_dropbox_user_settings(self):
        result = self.user.get_addon('dropbox')
        assert_true(isinstance(result, DropboxUserSettings))
