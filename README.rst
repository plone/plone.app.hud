=============
plone.app.hud
=============

This Plone add-on contains several HUD Panels:

* Best Practices - Plone best practices panel.
* Content Browser - browse through catalog.
* Security Advisories - RSS reader for `securiry advisories <http://plone.org/products/plone/security/advisories/>`_ directly inside Plone.
* Users - basic users information.


It uses `plone.hud framework <https://github.com/plone/plone.hud>`_


* `Source code @ GitHub <https://github.com/plone/plone.app.hud>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/plone.app.hud>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/plone/plone.app.hud>`_


Installation
============

To install `plone.app.hud` you simply add ``plone.app.hud``
to the list of eggs in your buildout.


Activation
----------

Run buildout and restart Plone.
Then, install `plone.app.hud` using the Add-ons control panel.


Usage
=====

Access the panels by adding `/@@hud` to the end of site URL, like so:

    http://localhost:8080/Plone/@@hud

Or by clicking `HUD Panels` in `Site Setup` page.


Configuration
=============

Every panel has it's own permission,
so that you can assign it to any role you wish.


How to make your own panels?
============================

* `collective.examples.hud @ GitHub <https://github.com/collective/collective.examples.hud>`_


Development
===========

Add to your Plone ``buildout.cfg``::

    ...
    eggs +=
        ...
        plone.hud
        plone.app.hud
    ...
    extensions += mr.developer
    sources = sources

    auto-checkout =
        plone.hud
        plone.app.hud

    [sources]
    plone.hud = git git://github.com/plone/plone.hud.git
    plone.app.hud = git git://github.com/plone/plone.app.hud.git
    ...

