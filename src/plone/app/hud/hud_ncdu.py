# -*- coding: utf-8 -*-
from Products.ATContentTypes.content.folder import ATFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.hud.panel import HUDPanelView
from plone.memoize.ram import RAMCacheAdapter
from plone.memoize.volatile import cache
from time import time
from zope.ramcache import ram

ncdu_cache = ram.RAMCache()
ncdu_cache.update(maxAge=86400, maxEntries=10)


class NCDUPanelView(HUDPanelView):
    panel_template = ViewPageTemplateFile('hud_ncdu.pt')

    def render(self):
        if "invalidate_cache" in self.request.form:
            ncdu_cache.invalidateAll()

        self.portal = api.portal.get()
        self.portal_id = self.portal.absolute_url_path()[1:]
        self.portal_path = self.portal.absolute_url_path()

        if "go" in self.request.form:
            self.path = self.request.form["go"]
        else:
            self.path = self.portal_path
        return self.panel_template()

    @cache(
        lambda method, self: "cache_key",
        get_cache=lambda fun, *args, **kwargs: RAMCacheAdapter(ncdu_cache)
    )
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

        path_list = self.path.split("/")[1:]
        self.clickable_path_list = []
        current_path = []
        for current_id in path_list:
            current_path += [current_id]
            self.clickable_path_list += [{
                "id": current_id,
                "path": "/" + "/".join(current_path)
            }]
        return result
