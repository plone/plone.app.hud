# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.hud.panel import HUDPanelView

import os


class BestPracticesPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_best_practices.pt')

    def render(self):
        portal = api.portal.get()
        self.zope_writable_files = self.check_write_permissions(
            portal.Control_Panel.getSOFTWARE_HOME()
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
        return roles_dict
