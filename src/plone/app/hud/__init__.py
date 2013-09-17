# -*- coding: utf-8 -*-
"""Init and utils."""

from DateTime import DateTime
from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plone.app.hud')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def get_filtered_users(by_days=None, by_group=None, by_role=None):
    link = "{0}/@@user-information?userid={{user_id}}".format(
        api.portal.get().absolute_url()
    )
    all_users = api.user.get_users()
    now = DateTime()
    users = []

    for user in all_users:
        add_user = False

        if by_days:
            value = int(by_days)
            login_date = DateTime(user.getProperty("login_time"))
            delta_days = now - login_date
            if (delta_days <= value) or \
                    (value == -1 and is_zero_DT(login_date)):
                add_user = True

        if by_group:
            user_groups = api.group.get_groups(user=user)
            group_names = [g.getGroupName() for g in user_groups]
            if by_group in group_names:
                add_user = True

        if by_role:
            user_roles = api.user.get_roles(user=user)
            role_names = [str(r) for r in user_roles]
            if by_role in role_names:
                add_user = True

        if add_user:
            users += [{
                "username": user.getUserName(),
                "fullname": user.getProperty("fullname"),
                "email": user.getProperty("email"),
                "link": link.format(user_id=user.getId())
            }]

    return users


def is_zero_DT(date):
    return date.year() == 2000 and date.month() == 1 and date.day() == 1
