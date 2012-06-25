# -*- coding: utf-8 -*-
import logging

from collective.grok import gs

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.upgrade import listUpgradeSteps

_PROJECT = 'conference.registration'
_PROFILE_ID = 'conference.registration:default'


@gs.importstep(name=u'conference.registration',
               title='Run upgrades for conference.registration',
               description='Run upgrades for conference.registration.')
def run_upgrades(context):
    """ Run Upgrade steps
    """
    if context.readDataFile('conference.registration-default.txt') is None:
        return
    logger = logging.getLogger(_PROJECT)
    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    version = setup_tool.getLastVersionForProfile(_PROFILE_ID)
    upgradeSteps = listUpgradeSteps(setup_tool, _PROFILE_ID, version)
    sorted(upgradeSteps, key=lambda step: step['sortkey'])

    for step in upgradeSteps:
        oStep = step.get('step')
        if oStep is not None:
            oStep.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" % (oStep.title,
                                                          _PROFILE_ID)
            setup_tool.setLastVersionForProfile(_PROFILE_ID, oStep.dest)
            logger.info(msg)
