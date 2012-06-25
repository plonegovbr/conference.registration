# -*- coding:utf-8 -*-
from five import grok

from collective.grok import gs
from collective.grok import i18n

from Products.CMFPlone.interfaces import INonInstallable

from conference.registration import MessageFactory as _

PROJECTNAME = 'conference.registration'
PROFILE_ID = 'conference.registration:default'


# Default Profile
gs.profile(name=u'default',
           title=_(u'conference.registration'),
           description=_(u'Installs conference.registration'),
           directory='profiles/default')

# Uninstall Profile
gs.profile(name=u'uninstall',
           title=_(u'Uninstall conference.registration'),
           description=_(u'Uninstall conference.registration'),
           directory='profiles/uninstall')

i18n.registerTranslations(directory='locales')


class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('conference.registration')

    def getNonInstallableProfiles(self):
        profiles = ['conference.registration:uninstall', ]
        return profiles
