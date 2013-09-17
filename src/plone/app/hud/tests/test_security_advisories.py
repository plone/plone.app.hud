# -*- coding: utf-8 -*-
"""Tests for security advisories panel."""

from plone.app.hud.testing import IntegrationTestCase

import mock
import os
import tempfile


class TestSecurityAdvisories(IntegrationTestCase):
    """Integration tests for security advisories panel."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.security_advisories = self.portal.unrestrictedTraverse(
            "@@hud_security"
        )
        self.feed_contents = """
<?xml version="1.0" encoding="utf-8" ?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
         xmlns="http://purl.org/rss/1.0/">

<channel rdf:about="http://some.link.xyz/RSS">
  <title>Plone Security Advisories</title>
  <link>http://some.link.xyz</link>
  <description></description>
  <image rdf:resource="http://some.link.xyz/logo.png"/>

  <items>
    <rdf:Seq>
        <rdf:li rdf:resource="http://some.link.xyz/hotfix-update-posted"/>
        <rdf:li rdf:resource="http://some.link.xyz/security-patch"/>
    </rdf:Seq>
  </items>

</channel>

  <item rdf:about="http://some.link.xyz/hotfix-update-posted">
    <title>20130618 Hotfix update posted</title>
    <link>http://some.link.xyz/hotfix-update-posted</link>
    <description>Version 1.3 of 20130618 released.</description>

    <dc:publisher>No publisher</dc:publisher>
    <dc:creator></dc:creator>
    <dc:rights></dc:rights>
    <dc:date>2013-07-02T13:50:09Z</dc:date>
    <dc:type>News Item</dc:type>
  </item>


  <item rdf:about="http://some.link.xyz/security-patch">
    <title>Security Patch Delayed until 2013-06-18</title>
    <link>http://some.link.xyz/security-patch</link>
    <description>download.zope.org server issues delaying hotfix</description>

    <dc:publisher>No publisher</dc:publisher>
    <dc:creator></dc:creator>
    <dc:rights></dc:rights>
    <dc:date>2013-06-11T14:23:24Z</dc:date>
    <dc:type>News Item</dc:type>
  </item>

</rdf:RDF>
        """

        self.feed_fd, self.feed_abs_path = tempfile.mkstemp()
        os.write(self.feed_fd, self.feed_contents)
        os.close(self.feed_fd)
        self.security_advisories.FEED_URL = self.feed_abs_path

    def tearDown(self):
        os.remove(self.feed_abs_path)

    def prepare_security_advisories_env(self, request_form={}):
        """Prepare all the variables for various tests.

        Also, optionally you can set 'request_form' (it must be dict type),
        this updates the values in the view.request.form,
        it does not remove any keys.
        """
        # we do not render any templates inside integration tests
        with mock.patch(
            'plone.app.hud.hud_security_advisories.'
            'SecurityAdvisoriesView.panel_template'
        ):
            self.security_advisories.request.form.update(request_form)
            self.security_advisories.render()

    def test_parsed_feed(self):
        self.prepare_security_advisories_env()

        for entry in self.security_advisories.feed_data:
            if entry['hash'] == '455ca55fc73efe03fad82a6180f4002d557c507e':
                self.assertEqual(
                    entry['link'], u'http://some.link.xyz/hotfix-update-posted'
                )
                self.assertIsNotNone(entry['localized_time'])
                self.assertEqual(
                    entry['marked_as_read'], False,
                )
                self.assertEqual(
                    entry['summary'], u'Version 1.3 of 20130618 released.',
                )
                self.assertEqual(
                    entry['title'], u'20130618 Hotfix update posted',
                )
                self.assertIsNotNone(entry['updated'])

            elif entry['hash'] == '0b9cbb1288b35a0f750d426f18d80d59d7df9e95':
                self.assertEqual(
                    entry['link'], u'http://some.link.xyz/security-patch'
                )
                self.assertIsNotNone(entry['localized_time'])
                self.assertEqual(
                    entry['marked_as_read'], False,
                )
                self.assertEqual(
                    entry['summary'],
                    u'download.zope.org server issues delaying hotfix',
                )
                self.assertEqual(
                    entry['title'],
                    u'Security Patch Delayed until 2013-06-18',
                )
                self.assertIsNotNone(entry['updated'])

            else:
                self.fail(
                    "This shouldn't happed, "
                    "it means that feed entry is changed or added."
                )

    def test_marked_as_read(self):
        self.prepare_security_advisories_env({
            "toggle_mark": "455ca55fc73efe03fad82a6180f4002d557c507e"
        })

        # find the correct entry
        correct_entry = None
        for entry in self.security_advisories.feed_data:
            if entry['hash'] == '455ca55fc73efe03fad82a6180f4002d557c507e':
                correct_entry = entry
                break

        # check that correct entry exists
        self.assertIsNotNone(correct_entry)

        # check if the code marked this entry as read
        self.assertTrue(correct_entry['marked_as_read'])
