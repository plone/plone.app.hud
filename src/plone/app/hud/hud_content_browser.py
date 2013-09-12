# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.hud import _
from plone.hud.panel import HUDPanelView
from plone.memoize.ram import RAMCacheAdapter
from plone.memoize.volatile import cache
from time import time
from zope.ramcache import ram

import datetime
import locale
import logging
import math
import pytz
import re

ITEMS_PER_PAGE = 50

content_browser_cache = ram.RAMCache()
content_browser_cache.update(maxAge=86400, maxEntries=10)
logger = logging.getLogger("plone.app.hud.hud_content_browser")


class ContentBrowserPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_content_browser.pt')
    title = _(u"Content Browser")

    def render(self):
        self.portal = api.portal.get()
        self.portal_id = self.portal.absolute_url_path()[1:]
        self.portal_path = self.portal.absolute_url_path()
        self.process_time = None
        self.portal_url = self.portal.absolute_url()
        self.group_url = (
            "{url}/@@usergroup-groupmembership?"
            "groupname={{groupid}}".format(
                url=self.portal_url
            )
        )
        self.user_url = (
            "{url}/@@user-information?userid={{userid}}".format(
                url=self.portal_url
            )
        )

        if "invalidate_cache" in self.request.form:
            content_browser_cache.invalidateAll()

        try:
            self.page_number = int(self.request.form["page_number"])
        except:
            self.page_number = 1

        if "go" in self.request.form:
            self.path = self.request.form["go"]
        else:
            self.path = self.portal_path

        self.workflows = self.parse_workflow_titles()
        return self.panel_template()

    @cache(
        lambda method, self: "cache_key",
        get_cache=lambda fun, *args, **kwargs: RAMCacheAdapter(
            content_browser_cache
        )
    )
    def _get_all_results(self):
        """Scans the catalog and returns all items in tree like structure.

        Return example:
        {
            'plone': {
                'children': {
                    'folder': {
                        'children': {},
                        'countall': 0,
                        'item': {
                            'id': 'folder',
                            'modified': '2013-09-02T00:10:50+02:00',
                            'path': '/plone/folder',
                            'rid': -894254351,
                            'size': 1.0,
                            'state': '',
                            'title': '',
                            'type': u'Folder',
                            'url': 'http://nohost/plone/folder'
                        }
                    }
                },
                'countall': 1,
                'item': {
                    'id': 'plone',
                    'modified': DateTime('2013/09/02 00:10:46.869194 GMT+2'),
                    'path': '/plone',
                    'rid': None,
                    'size': 1.0,
                    'state': None,
                    'title': u'Plone site',
                    'type': 'PloneSite',
                    'url': 'http://nohost/plone'
                }
            }
        }
        """
        start_time = time()
        logger.info("Scanning database ...")

        results = self.context.portal_catalog.searchResults()
        items = {
            self.portal_id: {
                "children": {},
                "item": {
                    "title": self.portal.title,
                    "url": self.portal.absolute_url(),
                    "path": self.portal_path,
                    "id": self.portal_id,
                    "rid": None,
                    "type": self.portal.__class__.__name__,
                    "size": 0,
                    "state": None,
                    "modified": self.portal.modified()
                },
                "countall": 0
            }
        }
        for brain in results:
            item = self.get_item(brain)
            self.add_item(item, items)

        self.recount(items[self.portal_id])

        end_time = time()
        self.process_time = "{0:.3f}".format(round(end_time - start_time, 3))
        logger.info(
            "End of database scan. Elapsed time is {0} seconds.".format(
                self.process_time
            )
        )
        return items

    def add_item(self, item, items):
        item_path_list = item["path"][1:].split("/")

        # find last known parent
        count_parents = 1
        current_parent = items[self.portal_id]
        for current_part in item_path_list[1:]:
            if current_part in current_parent["children"]:
                current_parent = current_parent["children"][current_part]
                count_parents += 1
            else:
                break

        # fill path
        tail_list = item_path_list[count_parents:]

        for tail_part in tail_list:
            current_parent["children"][tail_part] = {
                "children": {},
                "item": None,
                "countall": 0
            }
            current_parent = current_parent["children"][tail_part]

        # set actual item
        current_parent["item"] = item

    def recount(self, root):
        children = root["children"]
        if children:
            for child in children:
                subitems, size = self.recount(children[child])
                root["countall"] += subitems + 1
                root["item"]["size"] += size
            return root["countall"], root["item"]["size"]
        else:
            return 0, root["item"]["size"]

    def get_item(self, brain):
        item = {
            "title": brain.Title,
            "url": brain.getURL(),
            "path": brain.getPath(),
            "id": brain.getId,
            "rid": brain.getRID(),
            "type": brain.Type,
            "size": self.get_kbytes(brain.getObjSize),
            "state": self.workflows[str(brain.review_state)],
            "modified": brain.ModificationDate
        }
        return item

    def get_kbytes(self, size_in_text):
        """Parses the input string and returns kbytes as float."""
        matched = re.match(
            "^\D*(\d+[\.\,]?\d*)\s*([BKMGTbkmgt]{0,2}).*$",
            size_in_text
        )
        if matched is None:
            return None
        groups = matched.groups()

        s_size = groups[0]
        s_unit = groups[1].upper()
        units = {
            "": -1,
            "B": -1,
            "KB": 0,
            "MB": 1,
            "GB": 2,
            "TB": 3
        }
        f_size = locale.atof(s_size)
        kbytes = f_size * 10 ** (units[s_unit] * 3)
        return kbytes

    def filter_results_by_path(self):
        """Returns list of items in path.

        Results are sorted by modification date.
        Path is stored in self.path which is from self.request.form
        as POST argument named 'go'.

        Return example for path is '/plone/test-folder':
        [{'countall': 2,
          'item': {'id': 'sub-folder',
                   'modified': '2013-09-02T01:10:01+02:00',
                   'path': '/plone/test-folder/sub-folder',
                   'rid': -1810078016,
                   'size': 1.0,
                   'state': '',
                   'title': 'Sub Folder',
                   'type': u'Folder',
                   'url': 'http://nohost/plone/test-folder/sub-folder'}},
         {'countall': 0,
          'item': {'id': 'test-file',
                   'modified': '2013-09-02T01:10:01+02:00',
                   'path': '/plone/test-folder/test-file',
                   'rid': -1810078018,
                   'size': 0.0,
                   'state': '',
                   'title': 'Test File',
                   'type': u'File',
                   'url': 'http://nohost/plone/test-folder/test-file'}},
         {'countall': 0,
          'item': {'id': 'test-document',
                   'modified': '2013-09-02T01:10:01+02:00',
                   'path': '/plone/test-folder/test-document',
                   'rid': -1810078020,
                   'size': 0.0,
                   'state': '',
                   'title': 'Test Document',
                   'type': u'Page',
                   'url': 'http://nohost/plone/test-folder/test-document'}}]
        """
        results = self._get_all_results()
        path_list = self.path.split("/")[1:]
        root_item = results[self.portal_id]
        for str_id in path_list:
            if str_id in root_item["children"]:
                root_item = root_item["children"][str_id]
        items = []
        self.current_root = root_item
        for str_id in root_item["children"]:
            item = root_item["children"][str_id]["item"]
            countall = root_item["children"][str_id]["countall"]
            items += [{"countall": countall, "item": item}]
        items = sorted(items, key=lambda child: child["item"]["modified"])
        return items

    def get_list(self):
        """Method prepares variables for template and returns list of items.

        List of items is limited to number of 'ITEMS_PER_PAGE' items.
        Created variables to be used in template:
            - 'clickable_path_list':
                list of dictionaries with 'id' and 'path'
                path buttons are going to be rendered with this,
            - 'page_numbers' dictionary:
                template will use this for page location information
                Example:
                {
                    "first": 1,
                    "previous": 122,
                    "this": 123,
                    "next": 124,
                    "last": 200
                }
        """
        result = self.filter_results_by_path()

        path_list = self.path.split("/")[1:]
        self.clickable_path_list = []
        current_path = []
        for current_id in path_list:
            current_path += [current_id]
            self.clickable_path_list += [{
                "id": current_id,
                "path": "/" + "/".join(current_path)
            }]

        self.page_numbers = {
            "first": None,
            "previous": None,
            "this": None,
            "next": None,
            "last": None
        }
        start_item = ITEMS_PER_PAGE * (self.page_number - 1)
        if start_item <= 0:
            start_item = 0
            self.page_numbers["first"] = None
            self.page_numbers["previous"] = None
            self.page_numbers["this"] = "1"
        else:
            self.page_numbers["first"] = "1"
            self.page_numbers["previous"] = str(self.page_number - 1)
            self.page_numbers["this"] = str(self.page_number)
        end_item = start_item + ITEMS_PER_PAGE - 1
        last_item = len(result) - 1
        last_page = int(math.ceil((last_item + 1.0) / ITEMS_PER_PAGE))
        if end_item >= last_item:
            end_item = last_item
            self.page_numbers["this"] = str(last_page)
            self.page_numbers["next"] = None
            self.page_numbers["last"] = None
        else:
            self.page_numbers["next"] = str(self.page_number + 1)
            self.page_numbers["last"] = str(last_page)

        return result[start_item:end_item + 1]

    def format_datetime_friendly_ago(self, date):
        """ Format date & time using site specific settings.

        Source:
        http://developer.plone.org/misc/datetime.html
        """

        if date is None:
            return ""

        date = DateTime(date).asdatetime()  # zope DateTime -> python datetime

        # How long ago the timestamp is
        # See timedelta doc http://docs.python.org/lib/datetime-timedelta.html
        #since = datetime.datetime.utcnow() - date

        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)

        since = now - date

        seconds = since.seconds + since.microseconds / 1E6 + since.days * 86400

        days = math.floor(seconds / (3600 * 24))

        if days <= 0 and seconds <= 0:
            # Timezone confusion, is in future
            return _(u"moment ago")

        if days >= 1:
            return self.portal.toLocalizedTime(date)
        else:
            hours = math.floor(seconds / 3600.0)
            minutes = math.floor((seconds % 3600) / 60)
            if hours > 0:
                return "{0} {1} {2} {3}".format(
                    hours, _(u"hours"), minutes, _(u"minutes ago")
                )
            else:
                if minutes > 0:
                    return "{0} {1}".format(minutes, _(u"minutes ago"))
                else:
                    return _(u"few seconds ago")

    def parse_workflow_titles(self):
        workflow_tool = api.portal.get_tool('portal_workflow')
        wf_list = workflow_tool.listWFStatesByTitle()
        wf_dict = {
            "": ""
        }
        for wf_title, wf_id in wf_list:
            wf_dict[wf_id] = wf_title
        return wf_dict
