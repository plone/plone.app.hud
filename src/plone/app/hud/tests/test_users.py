# -*- coding: utf-8 -*-
"""Tests for users panel."""

from DateTime import DateTime
from plone import api
from plone.app.hud import get_filtered_users
from plone.app.hud.testing import IntegrationTestCase

import mock


class TestUsers(IntegrationTestCase):
    """Integration tests for users panel."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.users = self.portal.unrestrictedTraverse(
            "@@hud_users"
        )

        # prepare test users
        dt_now = DateTime()
        for i in range(1, 101):
            user = api.user.create(
                username="user{0}".format(i),
                email="user{0}@email.xyz".format(i)
            )
            if 20 >= i > 10:
                user.setMemberProperties(mapping={
                    'login_time': dt_now
                })
            elif 30 >= i > 20:
                user.setMemberProperties(mapping={
                    'login_time': dt_now - 6
                })
            elif 40 >= i > 30:
                user.setMemberProperties(mapping={
                    'login_time': dt_now - 30
                })
            elif 50 >= i > 40:
                user.setMemberProperties(mapping={
                    'login_time': dt_now - 365
                })
            elif 60 >= i > 50:
                api.group.add_user(user=user, groupname="Reviewers")

    def prepare_users_env(self, request_form={}):
        """Prepare all the variables for various tests.

        Also, optionally you can set 'request_form' (it must be dict type),
        this updates the values in the view.request.form,
        it does not remove any keys.
        """
        # we do not render any templates inside integration tests
        with mock.patch(
            'plone.app.hud.hud_users.'
            'UsersPanelView.panel_template'
        ):
            self.users.request.form.update(request_form)
            self.users.render()

    def test_process_all(self):
        self.prepare_users_env()

        self.assertEqual(self.users.count_users, 101)

        self.assertEqual(
            self.users.active_users,
            [
                {'user_count': 61, 'value': -1, 'title': u'Never'},
                {'user_count': 10, 'value': 1, 'title': u'Last day'},
                {'user_count': 20, 'value': 7, 'title': u'Last week'},
                {'user_count': 30, 'value': 31, 'title': u'Last month'},
                {'user_count': 40, 'value': 366, 'title': u'Last year'}
            ]
        )

        self.assertEqual(
            self.users.groups,
            {'Administrators': 0,
             'AuthenticatedUsers': 101,
             'Reviewers': 10,
             'Site Administrators': 0}
        )

    def test_filter_by_days(self):
        users = get_filtered_users(by_days=-1)
        self.assertEqual(len(users), 61)

        users = get_filtered_users(by_days=1)
        self.assertEqual(len(users), 10)

        users = get_filtered_users(by_days=7)
        self.assertEqual(len(users), 20)

        users = get_filtered_users(by_days=31)
        self.assertEqual(len(users), 30)

        users = get_filtered_users(by_days=366)
        self.assertEqual(len(users), 40)

    def test_filter_by_group(self):
        users = get_filtered_users(by_group="Reviewers")
        self.assertEqual(len(users), 10)

    def test_filter_by_role(self):
        users = get_filtered_users(by_role="Member")
        self.assertEqual(len(users), 100)
