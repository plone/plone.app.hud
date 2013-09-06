# -*- coding: utf-8 -*-
"""Tests for best practices panel."""

from plone import api
from plone.app.hud.testing import IntegrationTestCase

import os
import tempfile


class TestBestPractices(IntegrationTestCase):
    """Integration tests for best practices panel."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.best_practices = self.portal.unrestrictedTraverse(
            "@@hud_best_practices"
        )

    def test_check_write_permissions(self):
        # prepare environment
        tmpdirectory = tempfile.mkdtemp()

        with open(os.path.join(tmpdirectory, 'file0'), 'w') as f:
            f.write("File zero contents.")

        os.mkdir(os.path.join(tmpdirectory, 'empty_dir'))

        os.mkdir(os.path.join(tmpdirectory, 'somedir'))
        with open(os.path.join(tmpdirectory, 'somedir', 'file1'), 'w') as f:
            f.write("File one contents.")
        with open(os.path.join(tmpdirectory, 'somedir', 'file2'), 'w') as f:
            f.write("File two contents.")

        # run the method
        entries = self.best_practices.check_write_permissions(
            tmpdirectory
        )

        # test the results
        self.assertEqual(
            entries,
            [
                {
                    'absparentpath': tmpdirectory,
                    'whole_parent': True, 'contents': None
                }, {
                    'absparentpath': os.path.join(tmpdirectory, 'somedir'),
                    'whole_parent': True, 'contents': None
                }
            ]
        )

        # clean up
        for root, dirs, files in os.walk(tmpdirectory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmpdirectory)

        # check if cleanup was successful
        self.assertFalse(os.path.exists(tmpdirectory))

    def test_get_from_mail_address(self):

        # test email from address that is not set
        self.assertEqual(
            None,
            self.best_practices.get_from_mail_address()
        )

        # set email_from_address
        from zope.component import getUtility
        from Products.CMFCore.interfaces import ISiteRoot
        getUtility(ISiteRoot).email_from_address = 'ovce@xyz.xyz'

        # test email from address
        self.assertEqual(
            'ovce@xyz.xyz',
            self.best_practices.get_from_mail_address()
        )

    def test_count_users_with_roles(self):

        # test with basic test configuration of users
        entries = self.best_practices.count_users_with_roles()
        self.assertEqual(
            entries,
            {'Manager': 1}
        )

        # add two users with no roles for now
        api.user.create(email='ovce@xyz.xyz', username='ovce')
        api.user.create(email='koze@xyz.xyz', username='koze')

        # test that method is not outputting false information
        entries = self.best_practices.count_users_with_roles()
        self.assertEqual(
            entries,
            {'Manager': 1}
        )

        # grant roles for users
        api.user.grant_roles(
            username='ovce',
            roles=['Reviewer']
        )
        api.user.grant_roles(
            username='koze',
            roles=['Editor', 'Contributor', 'Reviewer']
        )

        # final test
        entries = self.best_practices.count_users_with_roles()
        self.assertEqual(
            entries,
            {'Manager': 1, 'Editor': 1, 'Contributor': 1, 'Reviewer': 2}
        )

    def test_get_broken_klasses(self):
        # test that method returns empty list
        # in test environment it should always return empty list
        self.assertEqual(
            [],
            self.best_practices.get_broken_klasses()
        )

    def test_check_caching(self):
        # set caching variables
        self.best_practices.check_caching()

        # test caching variables
        self.assertFalse(self.best_practices.is_caching_ok)
        self.assertFalse(self.best_practices.is_caching_installed)
        self.assertFalse(self.best_practices.is_caching_enabled)

    def test_check_oldest_transaction(self):
        # in testing environment this method should always return 0.0
        self.assertEqual(
            0.0,
            self.best_practices.check_oldest_transaction()
        )
