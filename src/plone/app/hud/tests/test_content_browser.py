# -*- coding: utf-8 -*-
"""Tests for content browser panel."""

from DateTime import DateTime
from plone import api
from plone.app.hud.hud_content_browser import ContentBrowserPanelView
from plone.app.hud.testing import IntegrationTestCase

import mock
import unittest2 as unittest


class TestContentBrowser(IntegrationTestCase):
    """Integration tests for content browser panel."""

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
        self.content_browser = self.portal.unrestrictedTraverse(
            "@@hud_content_browser"
        )
        self.content_browser.portal = self.portal

    def tearDown(self):
        """Clean up after each test."""
        api.content.delete(obj=self.portal['test-folder'])

    def prepare_content_browser_env(self, request_form={}):
        """Prepare all the variables for various tests.

        Also, optionally you can set 'request_form' (it must be dict type),
        this updates the values in the view.request.form,
        it does not remove any keys.
        """
        # we do not render any templates inside integration tests
        with mock.patch(
            'plone.app.hud.hud_content_browser.'
            'ContentBrowserPanelView.panel_template'
        ):
            self.content_browser.request.form.update(request_form)
            self.content_browser.render()

    def test_get_all_results(self):
        # prepare environment
        self.prepare_content_browser_env()

        # we are testing this method
        results = self.content_browser._get_all_results()

        # test the results
        self.assertIn('plone', results)
        self.assertEqual('plone', results['plone']['item']['id'])
        self.assertEqual(7, results['plone']['countall'])
        self.assertIn('test-folder', results['plone']['children'])

    def test_filter_results_by_path(self):
        # prepare environment
        self.prepare_content_browser_env(
            request_form={'go': '/plone/test-folder'}
        )

        # we are testing this method
        results = self.content_browser.filter_results_by_path()
        current_root = self.content_browser.current_root

        # test the results
        folder_ids = ['sub-folder', 'test-document', 'test-file']
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

        # test the current root object
        self.assertEqual(
            current_root["item"]["title"],
            "Test Folder"
        )
        self.assertEqual(
            current_root["countall"],
            5
        )

    def test_get_list(self):
        # prepare environment
        self.prepare_content_browser_env(
            request_form={'go': '/plone/test-folder'}
        )

        # we are testing this method
        results = self.content_browser.get_list()

        # test the results
        self.assertEqual(
            3,
            len(results)
        )

        # test clickable path list
        self.assertEqual(
            self.content_browser.clickable_path_list,
            [
                {'path': '/plone', 'id': 'plone'},
                {'path': '/plone/test-folder', 'id': 'test-folder'}
            ]
        )

        # test page numbers object
        self.assertEqual(
            self.content_browser.page_numbers,
            {
                'this': '1',
                'next': None,
                'previous': None,
                'last': None,
                'first': None
            }
        )


class TestContentBrowserUnitTests(unittest.TestCase):

    def setUp(self):
        self.content_browser = ContentBrowserPanelView(None, None)
        self.content_browser.portal = mock.Mock()

    def test_get_kbytes(self):
        self.assertEqual(
            self.content_browser.get_kbytes("3"),
            0.003
        )
        self.assertEqual(
            self.content_browser.get_kbytes("3B"),
            0.003
        )
        self.assertEqual(
            self.content_browser.get_kbytes("3 KB"),
            3.0
        )
        self.assertEqual(
            self.content_browser.get_kbytes("    3    MB   "),
            3000.0
        )
        self.assertEqual(
            self.content_browser.get_kbytes("garbage3GBgarbage"),
            3000000.0
        )
        self.assertEqual(
            self.content_browser.get_kbytes("garbage3  TBgarbage"),
            3000000000.0
        )

    def test_format_datetime_friendly_ago(self):
        dt_now = DateTime()

        # test now
        self.assertEqual(
            self.content_browser.format_datetime_friendly_ago(dt_now),
            u"few seconds ago"
        )

        # test future
        self.assertEqual(
            self.content_browser.format_datetime_friendly_ago(dt_now + 120),
            u"moment ago"
        )

        # test past
        self.content_browser.format_datetime_friendly_ago(dt_now - 120)
        self.assertTrue(
            self.content_browser.portal.toLocalizedTime.called
        )
