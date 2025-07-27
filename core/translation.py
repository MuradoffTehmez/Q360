# core/translation.py - Model Translation konfiqurasiyası

from modeltranslation.translator import register, TranslationOptions
from .models import (
    OrganizationUnit, SualKateqoriyasi, Sual, QiymetlendirmeDovru,
    QuickFeedbackCategory, IdeaCategory
)


@register(OrganizationUnit)
class OrganizationUnitTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(SualKateqoriyasi) 
class SualKateqoriyasiTranslationOptions(TranslationOptions):
    fields = ('ad',)


@register(Sual)
class SualTranslationOptions(TranslationOptions):
    fields = ('metn',)


@register(QiymetlendirmeDovru)
class QiymetlendirmeDovruTranslationOptions(TranslationOptions):
    fields = ('ad',)


@register(QuickFeedbackCategory)
class QuickFeedbackCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(IdeaCategory)
class IdeaCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

# Historical models
from .models import (
    HistoricalOrganizationUnit, HistoricalSualKateqoriyasi, HistoricalSual,
    HistoricalQiymetlendirmeDovru, HistoricalQuickFeedbackCategory, HistoricalIdea,
    HistoricalIdeaComment
)

@register(HistoricalOrganizationUnit)
class HistoricalOrganizationUnitTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(HistoricalSualKateqoriyasi)
class HistoricalSualKateqoriyasiTranslationOptions(TranslationOptions):
    fields = ('ad',)

@register(HistoricalSual)
class HistoricalSualTranslationOptions(TranslationOptions):
    fields = ('metn',)

@register(HistoricalQiymetlendirmeDovru)
class HistoricalQiymetlendirmeDovruTranslationOptions(TranslationOptions):
    fields = ('ad',)

@register(HistoricalQuickFeedbackCategory)
class HistoricalQuickFeedbackCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(HistoricalIdeaComment)
class HistoricalIdeaCommentTranslationOptions(TranslationOptions):
    fields = ()

@register(HistoricalIdea)
class HistoricalIdeaTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'estimated_impact', 'implementation_notes', 'review_notes')