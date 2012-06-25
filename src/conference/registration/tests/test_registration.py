# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from zope.schema.interfaces import IVocabularyFactory

from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.uuid.interfaces import IAttributeUUID

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from Products.CMFCore.utils import _checkPermission as checkPerm

from Products.CMFCore.WorkflowCore import WorkflowException

from conference.registration.content.registration import IRegistration

from conference.registration.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        self.registrations = self.portal['registrations']

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.registration')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.registration')
        schema = fti.lookupSchema()
        self.assertEquals(IRegistration, schema)

    def test_is_referenceable(self):
        self.registrations.invokeFactory('conference.registration',
                                         'guido')
        registration = self.registrations['guido']
        self.assertTrue(IReferenceable.providedBy(registration))
        self.assertTrue(IAttributeUUID.providedBy(registration))

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.registration')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IRegistration.providedBy(new_object))


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUpUsers(self):
        acl_users = self.portal.acl_users
        acl_users._doAddUser('Manager', 'secret', ['Manager'], [])
        acl_users._doAddUser('Member', 'secret', ['Member'], [])
        acl_users._doAddUser('Owner', 'secret', ['Owner'], [])
        acl_users._doAddUser('Reviewer', 'secret', ['Reviewer'], [])
        acl_users._doAddUser('Editor', 'secret', ['Editor'], [])

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = self.portal.portal_workflow
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.setUpUsers()
        self.portal.invokeFactory('conference.registrations',
                                  'registrations')
        self.registrations = self.portal['registrations']
        self.wf_tran(self.registrations, 'open')
        self.registrations.invokeFactory('conference.registration',
                                               'guido')
        self.reg = self.registrations['guido']

    def wf_state(self, obj):
        return self.wt.getInfoFor(obj, 'review_state')

    def wf_tran(self, obj, transition):
        try:
            self.wt.doActionFor(obj, transition)
            return self.wf_state(obj)
        except WorkflowException:
            raise

    def user(self, user):
        logout()
        login(self.portal, user)

    def test_initial_state(self):
        self.assertEquals(self.wf_state(self.reg), 'new')

    def test_member_submit_registration(self):
        self.user(TEST_USER_NAME)
        self.assertEquals(self.wf_tran(self.reg, 'submit'), 'pending')

    def test_member_cannot_confirm_registration(self):
        self.user(TEST_USER_NAME)
        self.assertRaises(WorkflowException, self.wf_tran,
                  *(self.registrations, 'confirm'))

    def test_editor_cannot_confirm_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Editor cannot confirm it
        self.user('Editor')
        self.assertRaises(WorkflowException, self.wf_tran,
                  *(self.registrations, 'confirm'))

    def test_reviewer_confirm_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Reviewer confirm it
        self.user('Reviewer')
        self.assertEquals(self.wf_tran(self.reg, 'confirm'), 'confirmed')

    def test_manager_confirm_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Reviewer confirm it
        self.user('Manager')
        self.assertEquals(self.wf_tran(self.reg, 'confirm'), 'confirmed')

    def test_member_cannot_cancel_registration(self):
        # Member not allowed to transition from new to cancelled
        self.user(TEST_USER_NAME)
        self.assertRaises(WorkflowException, self.wf_tran,
                  *(self.registrations, 'cancel'))
        # Reviewer will confirm registration
        self.user('Reviewer')
        self.wf_tran(self.reg, 'confirm')
        # Member not allowed to transition from confirmed to cancelled
        self.user(TEST_USER_NAME)
        self.assertRaises(WorkflowException, self.wf_tran,
                  *(self.registrations, 'cancel'))

    def test_editor_cannot_cancel_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Editor cannot cancel it
        self.user('Editor')
        self.assertRaises(WorkflowException, self.wf_tran,
                  *(self.registrations, 'cancel'))

    def test_reviewer_cancel_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Reviewer confirm it
        self.user('Reviewer')
        self.assertEquals(self.wf_tran(self.reg, 'cancel'), 'cancelled')

    def test_manager_cancel_registration(self):
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Reviewer confirm it
        self.user('Manager')
        self.assertEquals(self.wf_tran(self.reg, 'cancel'), 'cancelled')

    def test_view_permission_new_state(self):
        perm = 'View'
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_view_permission_pending_state(self):
        perm = 'View'
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_view_permission_confirmed_state(self):
        perm = 'View'
        # Manager confirm registration
        self.user('Manager')
        self.wf_tran(self.reg, 'confirm')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_view_permission_cancelled_state(self):
        perm = 'View'
        # Manager confirm registration
        self.user('Manager')
        self.wf_tran(self.reg, 'cancel')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_modify_permission_new_state(self):
        perm = 'Modify portal content'
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_modify_permission_pending_state(self):
        perm = 'Modify portal content'
        # Member submit registration
        self.user(TEST_USER_NAME)
        self.wf_tran(self.reg, 'submit')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertTrue(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_modify_permission_confirmed_state(self):
        perm = 'Modify portal content'
        # Manager confirm registration
        self.user('Manager')
        self.wf_tran(self.reg, 'confirm')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertFalse(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))

    def test_modify_permission_cancelled_state(self):
        perm = 'Modify portal content'
        # Manager confirm registration
        self.user('Manager')
        self.wf_tran(self.reg, 'cancel')
        # Check view permission
        self.user('Manager')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Editor')
        self.assertTrue(checkPerm(perm, self.reg))
        self.user('Member')
        self.assertFalse(checkPerm(perm, self.reg))
        self.user('Owner')
        self.assertFalse(checkPerm(perm, self.reg))
        logout()
        self.assertFalse(checkPerm(perm, self.reg))


class VocabulariesTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_registration_types(self):
        factory = queryUtility(IVocabularyFactory,
                               name='conference.registration.types')
        vocab = factory()
        self.assertNotEquals(vocab.by_token['basic'], None)
        self.assertEquals(vocab.by_token['basic'].title, 'Basic')
        self.assertEquals(vocab.by_token['student'].title, 'Student')

    def test_registration_tshirt_sizes(self):
        factory = queryUtility(IVocabularyFactory,
                               name='conference.registration.tshirt')
        vocab = factory()
        self.assertNotEquals(vocab.by_token['S'], None)
        self.assertEquals(vocab.by_token['S'].title, 'Small')
        self.assertEquals(vocab.by_token['L'].title, 'Large')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
