from django.db import models
from django.utils.translation import gettext_lazy as _


class ProvincesEnum(models.TextChoices):
    ANTWERPEN = "ANT", _("Antwerpen")
    HENEGOUWEN = "HAI", _("Henegouwen")
    LUIK = "LIE", _("Luik")
    LIMBURG = "LIM", _("Limburg")
    LUXEMBURG = "LUX", _("Luxemburg")
    NAMEN = "NAM", _("Namen")
    OOST_VLAANDEREN = "OVL", _("Oost-Vlaanderen")
    WEST_VLANDEREN = "WVL", _("West-Vlaanderen")
    VLAAMS_BRABANT = "VBR", _("Vlaams-Brabant")
    WAALS_BRABANT = "WBR", _("Waals-Brabant")

    __empty__ = _("(Unknown)")


class ValutasEnum(models.TextChoices):
    EURO = "EUR", _("Euro")
    DOLLAR = "USD", _("Dollar")
    POUND = "GBP", _("Pound")


class DaysOfTheWeekEnum(models.IntegerChoices):
    MONDAY = 0, _("Monday")
    TUESDAY = 1, _("Tuesday")
    WEDNESDAY = 2, _("Wednesday")
    THURSDAY = 3, _("Thursday")
    FRIDAY = 4, _("Friday")
    SATURDAY = 5, _("Saturday")
    SUNDAY = 6, _("Sunday")
