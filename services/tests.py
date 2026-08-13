"""Проверки постоянного ритма недели — той полосы, что стоит под первым экраном."""

from django.test import TestCase

from .models import (
    RecurringServiceItem,
    RecurringServiceRule,
    ServiceType,
    weekly_rhythm,
)


class WeeklyRhythmTests(TestCase):
    def setUp(self):
        self.liturgy = ServiceType.objects.create(name="Литургия")
        self.hours = ServiceType.objects.create(name="Часы", order=1)
        self.vigil = ServiceType.objects.create(name="Всенощное бдение", order=2)

    def rule(self, weekday, *items, active=True, title="Правило"):
        r = RecurringServiceRule.objects.create(
            weekday=weekday, title=title, is_active=active
        )
        for order, (service_type, time) in enumerate(items):
            RecurringServiceItem.objects.create(
                rule=r, service_type=service_type, time=time, order=order
            )
        return r

    def test_empty_when_no_rules(self):
        """Пустой шаблон — полосы на странице просто нет, а не пустая плашка."""
        self.assertEqual(weekly_rhythm(), [])

    def test_sunday_comes_first(self):
        """Литургия важнее понедельника: иначе приход с правилом на каждый день
        показал бы в полосе три будних дня и потерял воскресенье."""
        self.rule(0, (self.liturgy, "08:00"))
        self.rule(1, (self.liturgy, "08:00"))
        self.rule(5, (self.vigil, "18:00"))
        self.rule(6, (self.liturgy, "09:30"))

        labels = [row["label"] for row in weekly_rhythm()]
        self.assertEqual(
            [str(x) for x in labels],
            ["По воскресеньям", "По субботам", "По понедельникам"],
        )

    def test_inactive_rule_is_ignored(self):
        self.rule(6, (self.liturgy, "09:30"), active=False)
        self.assertEqual(weekly_rhythm(), [])

    def test_rule_without_services_is_ignored(self):
        """Заведённое, но не наполненное правило — не строка «По средам:» ни о чём."""
        self.rule(2)
        self.rule(6, (self.liturgy, "09:30"))

        rows = weekly_rhythm()
        self.assertEqual(len(rows), 1)
        self.assertEqual(str(rows[0]["label"]), "По воскресеньям")

    def test_services_keep_their_order(self):
        self.rule(6, (self.hours, "09:00"), (self.liturgy, "09:30"))

        names = [s["name"] for s in weekly_rhythm()[0]["services"]]
        self.assertEqual(names, ["Часы", "Литургия"])

    def test_limit_caps_the_strip(self):
        for weekday in range(7):
            self.rule(weekday, (self.liturgy, "08:00"))
        self.assertEqual(len(weekly_rhythm()), 3)
        self.assertEqual(len(weekly_rhythm(limit=5)), 5)
