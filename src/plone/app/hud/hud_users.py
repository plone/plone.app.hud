# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.hud import _
from plone.app.hud import get_filtered_users
from plone.app.hud import is_zero_DT
from plone.hud.panel import HUDPanelView


class UsersPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_users.pt')
    title = _(u"Users")

    def render(self):
        self.all_users = api.user.get_users()
        self.now = DateTime()
        self.days_list = [
            (_(u"Last day"), 1),
            (_(u"Last week"), 7),
            (_(u"Last month"), 31),
            (_(u"Last year"), 366),
            (_(u"Never"), -1)
        ]

        if "filter_by_days" in self.request.form:
            self.value = self.request.form["filter_by_days"]
            self.filter_title = self.get_day_filter_title(self.value)
            self.users = get_filtered_users(by_days=self.value)
            return ViewPageTemplateFile('hud_list_users.pt')(self)

        self.count_users = len(self.all_users)
        self.process_all(days_list=self.days_list)
        return self.panel_template()

    def get_day_filter_title(self, value):
        for dtitle, dvalue in self.days_list:
            if value == str(dvalue):
                return dtitle
        return str(value)

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
        active_list = sorted(
            active_list,
            key=lambda x: x["value"],
        )

        all_groups = api.group.get_groups()
        for group in all_groups:
            group_name = group.getGroupName()
            groups_dict[group_name] = 0

        for user in self.all_users:

            login_date = DateTime(user.getProperty("login_time"))
            delta_days = self.now - login_date
            for days_dict in active_list:
                if delta_days <= days_dict["value"]:
                    days_dict["user_count"] += 1
                if days == -1 and is_zero_DT(login_date):
                    days_dict["user_count"] += 1
                    break

            groups = api.group.get_groups(user=user)
            for group in groups:
                group_name = group.getGroupName()
                groups_dict[group_name] += 1

        self.active_users = active_list
        self.groups = groups_dict

    def get_group_url(self, groupname):
        return "{0}/@@usergroup-groupmembership?groupname={1}".format(
            api.portal.get().absolute_url(),
            groupname
        )
