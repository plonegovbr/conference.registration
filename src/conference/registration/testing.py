# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import collective.person
        self.loadZCML(package=collective.person)
        import conference.registration
        self.loadZCML(package=conference.registration)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'conference.registration:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='conference.registration:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='conference.registration:Functional',
    )
