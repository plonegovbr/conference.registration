# -*- coding:utf-8 -*-
from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from conference.registration import MessageFactory as _


class TShirtSizesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self):
        terms = [('S', _(u'Small')),
                 ('M', _(u'Medium')),
                 ('L', _(u'Large')),
                 ('X', _(u'X-Large'))]
        vocab = SimpleVocabulary(
                        [SimpleTerm(value=v, title=t) for v, t in terms])
        return vocab


grok.global_utility(TShirtSizesVocabulary,
                    name=u"conference.registration.tshirt")


class RegTypesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self):
        terms = [('basic', _(u'Basic')),
                 ('student', _(u'Student'))]
        vocab = SimpleVocabulary(
                        [SimpleTerm(value=v, title=t) for v, t in terms])
        return vocab


grok.global_utility(RegTypesVocabulary,
                    name=u"conference.registration.types")


class PaymentServicesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self):
        terms = [('no-payment', _(u'No Payment')), ]
        vocab = SimpleVocabulary(
                        [SimpleTerm(value=v, title=t) for v, t in terms])
        return vocab


grok.global_utility(PaymentServicesVocabulary,
                    name=u"conference.registration.paymentservices")
