# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone.app.hud.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of plone.app.hud into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if plone.app.hud is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('plone.app.hud'))

    def test_uninstall(self):
        """Test if plone.app.hud is cleanly uninstalled."""
        self.installer.uninstallProducts(['plone.app.hud'])
        self.assertFalse(self.installer.isProductInstalled('plone.app.hud'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneAppHudLayer is registered."""
        from plone.app.hud.interfaces import IPloneAppHudLayer
        from plone.browserlayer import utils
        self.failUnless(IPloneAppHudLayer in utils.registered_layers())
