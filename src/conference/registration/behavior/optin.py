# -*- coding:utf-8 -*-
from zope.interface import alsoProvides
from zope import schema
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from conference.registration import MessageFactory as _


class IOptInInformation(form.Schema):
    """
        Marker/Form interface for OptIn information
    """
    conference = schema.Bool(
                 title=_(u'Accept to be contacted by conference organizers'),
                 default=True,
                 required=False,
    )

    partners = schema.Bool(
                title=_(u'Accept to be contacted by conference partners'),
                default=True,
                required=False,
    )


alsoProvides(IOptInInformation, IFormFieldProvider)
