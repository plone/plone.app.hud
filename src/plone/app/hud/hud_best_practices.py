# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.hud import _
from plone.hud.panel import HUDPanelView

import os


class BestPracticesPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_best_practices.pt')
    title = _(u"Best Practices")

    # ZODB should be packed at least every 'PACK_DAYS' days
    PACK_DAYS = 30

    def render(self):
        self.portal = api.portal.get()
        self.zope_writable_files = self.check_write_permissions(
            self.portal.Control_Panel.getSOFTWARE_HOME()
        )
        self.check_caching()

        self.days_from_oldest_undo = self.check_oldest_undo()
        self.is_pack_time = self.days_from_oldest_undo > self.PACK_DAYS
        self.formatted_days_from_oldest_undo = "{0:.1f}".format(
            self.check_oldest_undo()
        )

        return self.panel_template()

    def check_write_permissions(self, directory):
        w_entries = []
        for parentpath, dirnames, filenames in os.walk(directory):
            absparentpath = os.path.abspath(parentpath)
            items = []
            whole_parent = True

            # check all directories
            for dirname in dirnames:
                dirpath = os.path.join(absparentpath, dirname)
                if os.access(dirpath, os.W_OK):
                    items += [dirpath + os.sep]
                else:
                    whole_parent = False

            # check all files
            for filename in filenames:
                filepath = os.path.join(absparentpath, filename)
                if os.access(filepath, os.W_OK):
                    items += [filepath]
                else:
                    whole_parent = False

            if not items:
                continue

            # store information
            w_entries += [
                {
                    "absparentpath": absparentpath,
                    "whole_parent": whole_parent,
                    "contents": None if whole_parent else items,
                }
            ]

        return w_entries

    def get_from_mail_address(self):
        email_from_address = api.portal.get().getProperty('email_from_address')
        return email_from_address if email_from_address else None

    def count_users_with_roles(self):
        roles_dict = {}
        all_users = api.user.get_users()
        for user in all_users:
            users_roles = api.user.get_roles(user=user)
            for role in users_roles:
                if role in roles_dict:
                    roles_dict[role] += 1
                else:
                    roles_dict[role] = 1
        del roles_dict['Authenticated']
        del roles_dict['Member']
        return roles_dict

    def get_broken_klasses(self):
        import OFS.Uninstalled
        broken_klasses = OFS.Uninstalled.broken_klasses.keys()
        result = []
        for kmodule, kname in broken_klasses:
            result += [{
                "module": kmodule,
                "name": kname
            }]
        return result

    def check_caching(self):
        self.installer = api.portal.get_tool('portal_quickinstaller')

        self.is_caching_installed = \
            self.installer.isProductInstalled('plone.app.caching')

        registry = api.portal.get_tool('portal_registry')
        if registry.get('plone.caching.interfaces.ICacheSettings.enabled'):
            self.is_caching_enabled = True
        else:
            self.is_caching_enabled = False

        self.is_caching_ok = \
            self.is_caching_installed and self.is_caching_enabled

    def check_oldest_undo(self):
        undo_tool = api.portal.get_tool("portal_undo")
        undo_list = undo_tool.listUndoableTransactionsFor(self.portal)

        now = DateTime()
        oldest_undo = now

        for item in undo_list:
            if item["time"] < oldest_undo:
                oldest_undo = item["time"]

        return now - oldest_undo
