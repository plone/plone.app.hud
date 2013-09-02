# -*- coding: utf-8 -*-
"""Tests for NCDU panel."""

from plone import api
from plone.app.hud.testing import IntegrationTestCase

import mock


class TestNCDU(IntegrationTestCase):
    """Integration tests for NCDU panel."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        # create content items
        folder = api.content.create(
            type='Folder',
            title='Test Folder',
            container=self.portal
        )
        api.content.create(
            type='Document',
            title='Test Document',
            container=folder
        )
        api.content.create(
            type='File',
            title='Test File',
            container=folder
        )
        sub_folder = api.content.create(
            type='Folder',
            title='Sub Folder',
            container=folder
        )
        api.content.create(
            type='Document',
            title='Test Document One',
            container=sub_folder
        )
        api.content.create(
            type='Document',
            title='Test Document Two',
            container=sub_folder
        )

        # get view
        self.ncdu = self.portal.unrestrictedTraverse(
            "@@hud_ncdu"
        )

    def tearDown(self):
        """Clean up after each test."""
        api.content.delete(obj=self.portal['test-folder'])

    def prepare_ncdu_env(self, request_form={}):
        """Prepare all the variables for various tests.

        Also, optionally you can set 'request_form' (it must be dict type),
        this updates the values in the view.request.form,
        it does not remove any keys.
        """
        # we do not render any templates inside integration tests
        with mock.patch(
            'plone.app.hud.hud_ncdu.NCDUPanelView.panel_template'
        ):
            self.ncdu.request.form.update(request_form)
            self.ncdu.render()

    def test_get_all_results(self):
        # prepare environment
        self.prepare_ncdu_env()

        # we are testing this method
        results = self.ncdu._get_all_results()

        # test the results
        self.assertIn('plone', results)
        self.assertEqual('plone', results['plone']['item']['id'])
        self.assertEqual(7, results['plone']['countall'])
        self.assertIn('test-folder', results['plone']['children'])

    def test_filter_results_by_path(self):
        # prepare environment
        self.prepare_ncdu_env(request_form={'go': '/plone/test-folder'})

        # we are testing this method
        results = self.ncdu.filter_results_by_path()

        folder_ids = ['sub-folder', 'test-document', 'test-file']

        # test the results
        self.assertEqual(
            3,
            len(results)
        )
        self.assertIn(
            results[0]['item']['id'],
            folder_ids
        )
        self.assertIn(
            results[1]['item']['id'],
            folder_ids
        )
        self.assertIn(
            results[2]['item']['id'],
            folder_ids
        )

    def test_get_list(self):
        # prepare environment
        self.prepare_ncdu_env(request_form={'go': '/plone/test-folder'})

        # we are testing this method
        results = self.ncdu.get_list()

        # TODO
