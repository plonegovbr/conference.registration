# -*- coding:utf-8 -*-
from five import grok

from zope import schema

from zope.component import getMultiAdapter

from plone.directives import dexterity
from plone.directives import form

from collective.person.content.person import gender_options

from conference.registration import MessageFactory as _


class IRegistration(form.Schema):
    """
    A registration in the conference
    """
    registration_type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Select the category of your registration'),
        required=False,
        vocabulary="conference.registration.types",
    )

    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )

    badge_name = schema.TextLine(
        title=_(u'Badge name'),
        description=_(u'Please inform the name that will appear on your badge'
                      u' -- Leave it blank to use your fullname in the badge'),
        required=False,
        missing_value=u'',
    )

    organization = schema.TextLine(
        title=_(u'Organization'),
        description=_(u'Please inform the name of the organization you'
                      u'will represent'),
        required=False,
        missing_value=u'',
    )

    gender = schema.Choice(
        title=_(u'Gender'),
        required=True,
        vocabulary=gender_options,
    )

    location = schema.TextLine(
        title=_(u'Location'),
        description=_(u'Please inform the city you are from.'),
        required=False,
        missing_value=u'',
    )

    t_shirt_size = schema.Choice(
        title=_(u'T-Shirt Size'),
        required=True,
        vocabulary="conference.registration.tshirt",
    )


class Registration(dexterity.Container):
    grok.implements(IRegistration)
    # Add your class methods and properties here

    exclude_from_nav = True


@form.default_value(field=IRegistration['gender'])
def default_gender(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('gender')


@form.default_value(field=IRegistration['badge_name'])
@form.default_value(field=IRegistration['fullname'])
def default_fullname(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('fullname')


@form.default_value(field=IRegistration['location'])
def default_location(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('location')
