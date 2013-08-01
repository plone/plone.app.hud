# -*- coding: utf-8 -*-
from Products.ATContentTypes.content.folder import ATFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.hud.panel import HUDPanelView
from plone.memoize.ram import cache
from plone.registry import Record
from plone.registry import Registry
from plone.registry import field
from time import time


class NCDUPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_ncdu.pt')
    registry = Registry()
    clear_cache_name = "plone.app.hud.hud_ncdu.clear_cache"

    def render(self):
        if "invalidate_cache" in self.request.form:
            self.invalidate_cache()

        self.portal = api.portal.get()
        self.portal_id = self.portal.absolute_url_path()[1:]
        self.portal_path = self.portal.absolute_url_path()

        if "go" in self.request.form:
            self.path = self.request.form["go"]
        else:
            self.path = self.portal_path
        return self.panel_template()

    def cache_key(method, self):
        if not self.clear_cache_name in self.registry:
            clear_cache_field = field.Text(title=u"Clear Cache")
            clear_cache_record = Record(clear_cache_field)
            clear_cache_record.value = unicode(time())
            self.registry.records[self.clear_cache_name] = clear_cache_record
        return self.registry[self.clear_cache_name]

    def invalidate_cache(self):
        self.registry[self.clear_cache_name] = unicode(time())

    @cache(cache_key)
    def _get_all_results(self):
        results = self.context.portal_catalog.searchResults()
        items = {
            self.portal_id: {
                "children": {},
                "item": {
                    "url": self.portal.absolute_url(),
                    "path": self.portal_path,
                    "id": self.portal_id,
                    "rid": None,
                    "type": self.portal.__class__.__name__,
                    "is_folder": True,
                    # "count": len(self.portal.listFolderContents()),
                },
                "countall": 0
            }
        }
        for brain in results:
            item = self.get_item(brain)
            self.add_item(item, items)

        self.recount(items[self.portal_id])
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
                root["countall"] += self.recount(children[child]) + 1
            return root["countall"]
        else:
            return 0

    def get_item(self, brain):
        obj = brain.getObject()
        is_folder = isinstance(obj, ATFolder)
        item = {
            "url": brain.getURL(),
            "path": brain.getPath(),
            "id": brain.getId,
            "rid": brain.getRID(),
            "type": obj.__class__.__name__,
            "is_folder": is_folder,
        }
        return item

    def filter_results_by_path(self):
        results = self._get_all_results()
        path_list = self.path.split("/")[1:]
        root_item = results[self.portal_id]
        for str_id in path_list:
            if str_id in root_item["children"]:
                root_item = root_item["children"][str_id]
        items = []
        for str_id in root_item["children"]:
            item = root_item["children"][str_id]["item"]
            countall = root_item["children"][str_id]["countall"]
            # if item is not None:
            items += [{"countall": countall, "item": item}]
        return items

    def get_list(self):
        start_time = time()
        result = self.filter_results_by_path()
        end_time = time()
        self.process_time = end_time - start_time
        return result
