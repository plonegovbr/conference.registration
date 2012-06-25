# -*- coding: utf-8 -*-
import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from Products.CMFCore.utils import _checkPermission as checkPerm

from Products.CMFCore.WorkflowCore import WorkflowException

from conference.registration.content.registrations import IRegistrationFolder

from conference.registration.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.registrations')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.registrations')
        schema = fti.lookupSchema()
        self.assertEquals(IRegistrationFolder, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.registrations')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IRegistrationFolder.providedBy(new_object))

    def test_registrations_contraints(self):
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        registrations = self.portal['registrations']
        #registrations.invokeFactory('conference.registration', 'guido')
        self.assertRaises(ValueError, registrations.invokeFactory,
                          *('Folder', 'sub-folder'))
        self.assertRaises(ValueError, registrations.invokeFactory,
                          *('Document', 'page'))

    def test_add_as_manager(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        registrations = self.portal['registrations']
        self.assertEquals(registrations.portal_type,
                          'conference.registrations')

    def test_add_as_editor(self):
        setRoles(self.portal, TEST_USER_ID, ['Editor'])
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        registrations = self.portal['registrations']
        self.assertEquals(registrations.portal_type,
                          'conference.registrations')

    def test_add_as_contributor(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        self.assertRaises(Unauthorized, self.portal.invokeFactory,
                          *('conference.registrations', 'registrations'))

    def test_add_as_member(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized, self.portal.invokeFactory,
                          *('conference.registrations', 'registrations'))

    def test_add_as_anonymous(self):
        logout()
        self.assertRaises(Unauthorized, self.portal.invokeFactory,
                          *('conference.registrations', 'registrations'))


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = self.portal.portal_workflow
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        self.registrations = self.portal['registrations']

    def wf_state(self, obj):
        return self.wt.getInfoFor(obj, 'review_state')

    def wf_tran(self, obj, transition):
        try:
            self.wt.doActionFor(obj, transition)
            return self.wf_state(obj)
        except WorkflowException:
            raise

    def open_registrations(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wf_tran(self.registrations, 'open')

    def roles(self, roles):
        setRoles(self.portal, TEST_USER_ID, roles)

    def test_initial_state(self):
        self.assertEquals(self.wf_state(self.registrations), 'closed')

    def test_open_registrations_as_manager(self):
        self.roles(['Manager'])
        self.assertEquals(self.wf_tran(self.registrations, 'open'), 'opened')

    def test_open_registrations_as_reviewer(self):
        self.roles(['Reviewer'])
        self.assertEquals(self.wf_tran(self.registrations, 'open'), 'opened')

    def test_open_registrations_as_editor(self):
        self.roles(['Editor'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'open'))

    def test_open_registrations_as_contributor(self):
        self.roles(['Contributor'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'open'))

    def test_open_registrations_as_member(self):
        self.roles(['Member'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'open'))

    def test_close_registrations_as_manager(self):
        self.open_registrations()
        self.roles(['Manager'])
        self.assertEquals(self.wf_tran(self.registrations, 'close'), 'closed')

    def test_close_registrations_as_reviewer(self):
        self.open_registrations()
        self.roles(['Reviewer'])
        self.assertEquals(self.wf_tran(self.registrations, 'close'), 'closed')

    def test_close_registrations_as_editor(self):
        self.open_registrations()
        self.roles(['Editor'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'close'))

    def test_close_registrations_as_contributor(self):
        self.open_registrations()
        self.roles(['Contributor'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'close'))

    def test_close_registrations_as_member(self):
        self.open_registrations()
        self.roles(['Member'])
        self.assertRaises(WorkflowException, self.wf_tran,
                          *(self.registrations, 'close'))

    def test_view_permission_opened_state(self):
        perm = 'View'
        self.open_registrations()
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertTrue(checkPerm(perm, self.registrations))
        logout()
        self.assertTrue(checkPerm(perm, self.registrations))

    def test_modify_permission_opened_state(self):
        perm = 'Modify portal content'
        self.open_registrations()
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertFalse(checkPerm(perm, self.registrations))
        logout()
        self.assertFalse(checkPerm(perm, self.registrations))

    def test_add_registration_permission_opened_state(self):
        perm = 'conference.registration: Add Registration'
        self.open_registrations()
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertTrue(checkPerm(perm, self.registrations))
        logout()
        self.assertFalse(checkPerm(perm, self.registrations))

    def test_view_permission_closed_state(self):
        perm = 'View'
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertTrue(checkPerm(perm, self.registrations))
        logout()
        self.assertTrue(checkPerm(perm, self.registrations))

    def test_modify_permission_closed_state(self):
        perm = 'Modify portal content'
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertFalse(checkPerm(perm, self.registrations))
        logout()
        self.assertFalse(checkPerm(perm, self.registrations))

    def test_add_registration_permission_closed_state(self):
        perm = 'conference.registration: Add Registration'
        self.roles(['Manager'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Reviewer'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Editor'])
        self.assertTrue(checkPerm(perm, self.registrations))
        self.roles(['Contributor'])
        self.assertFalse(checkPerm(perm, self.registrations))
        self.roles(['Member'])
        self.assertFalse(checkPerm(perm, self.registrations))
        logout()
        self.assertFalse(checkPerm(perm, self.registrations))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
