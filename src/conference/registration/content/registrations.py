# -*- coding:utf-8 -*-
from five import grok

from plone.directives import dexterity
from plone.directives import form


class IRegistrationFolder(form.Schema):
    """
    A folder containing all registrations for the conference
    """


class RegistrationFolder(dexterity.Container):
    grok.implements(IRegistrationFolder)
    # Add your class methods and properties here
