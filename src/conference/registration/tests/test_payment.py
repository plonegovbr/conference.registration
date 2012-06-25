# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.behavior.interfaces import IBehavior

from conference.registration.behavior.payment import IPaymentInformation

from conference.registration.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    name = 'conference.registration.behavior.payment.IPaymentInformation'

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        self.registrations = self.portal['registrations']

    def test_registration(self):
        registration = queryUtility(IBehavior, name=self.name)
        self.assertNotEquals(None, registration)

    def test_adapt_registration(self):
        self.registrations.invokeFactory('conference.registration', 'guido')
        reg = self.registrations['guido']
        adapter = IPaymentInformation(reg)
        self.assertNotEquals(None, adapter)

    def test_store_payment_info(self):
        self.registrations.invokeFactory('conference.registration', 'guido')
        reg = self.registrations['guido']
        adapter = IPaymentInformation(reg)
        adapter.service = 'no-payment'
        adapter.paid = False
        adapter.amount = 0
        self.assertEquals(adapter.service, 'no-payment')
        self.assertEquals(adapter.paid, False)
        self.assertEquals(adapter.amount, 0)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
