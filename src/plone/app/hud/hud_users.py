# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.hud.panel import HUDPanelView

import urllib


class UsersPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_users.pt')

    def render(self):
        self.all_users = api.user.get_users()
        self.zero_date = DateTime('2000/01/01 00:00:00 GMT+1')
        self.now = DateTime()

        if "filter_by_days" in self.request.form:
            self.value = self.request.form["filter_by_days"]
            self.title = "Filtered by {0} days".format(self.value)
            self.users = self.get_filtered_users(by_days=self.value)
            return ViewPageTemplateFile('hud_list_users.pt')(self)

        elif "filter_by_group" in self.request.form:
            value = self.request.form["filter_by_group"]
            self.value = urllib.unquote(value)
            self.title = "Filtered by {0} group".format(self.value)
            self.users = self.get_filtered_users(by_group=self.value)
            return ViewPageTemplateFile('hud_list_users.pt')(self)

        self.count_users = len(self.all_users)
        days_list = [
            ("Last day", 1),
            ("Last week", 7),
            ("Last month", 31),
            ("Last year", 366),
            ("Never", -1)
        ]
        self.process_all(days_list=days_list)
        return self.panel_template()

    def process_all(self, days_list):
        active_list = []
        groups_dict = {}

        # initialize dictionary with zeros
        for days_title, days in days_list:
            active_list += [{
                "title": days_title,
                "value": days,
                "user_count": 0
            }]

        all_groups = api.group.get_groups()
        for group in all_groups:
            group_name = group.getGroupName()
            groups_dict[group_name] = 0

        for user in self.all_users:

            login_date = DateTime(user.getProperty("login_time"))
            delta_days = self.now - login_date
            for days_dict in active_list:
                if (delta_days <= days_dict["value"]) or \
                        (days == -1 and self.zero_date == login_date):
                    days_dict["user_count"] += 1

            groups = api.group.get_groups(user=user)
            for group in groups:
                group_name = group.getGroupName()
                groups_dict[group_name] += 1

        self.active_users = active_list
        self.groups = groups_dict

    def get_filtered_users(self, by_days=None, by_group=None):
        link = "{0}/@@user-information?userid={{user_id}}".format(
            api.portal.get().absolute_url()
        )
        users = []

        for user in self.all_users:
            add_user = False

            if by_days:
                value = int(by_days)
                login_date = DateTime(user.getProperty("login_time"))
                delta_days = self.now - login_date
                if (delta_days <= value) or \
                        (value == -1 and self.zero_date == login_date):
                    add_user = True

            if by_group:
                user_groups = api.group.get_groups(user=user)
                group_names = [g.getGroupName() for g in user_groups]
                if by_group in group_names:
                    add_user = True

            if add_user:
                users += [{
                    "username": user.getUserName(),
                    "fullname": user.getProperty("fullname"),
                    "email": user.getProperty("email"),
                    "link": link.format(user_id=user.getId())
                }]

        return users
