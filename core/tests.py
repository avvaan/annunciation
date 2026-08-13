"""Проверки страницы треб и тех блоков главной, что на неё ссылаются."""

from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings
from .trebas import TREBAS
from .worship import PARISH_LIFE, WORSHIP


class TrebasPageTests(TestCase):
    def test_page_lists_every_treba(self):
        response = self.client.get(reverse("core:trebas"))
        self.assertEqual(response.status_code, 200)
        for treba in TREBAS:
            self.assertContains(response, str(treba["title"]))

    def test_every_treba_has_an_anchor(self):
        page = self.client.get(reverse("core:trebas")).content.decode()
        for treba in TREBAS:
            self.assertIn(f'id="{treba["slug"]}"', page, f"нет якоря для {treba['slug']}")

    def test_slugs_are_unique(self):
        """Slug — и адрес якоря, и ключ правленого текста в PageText:
        совпадение молча склеило бы два описания в одно."""
        slugs = [t["slug"] for t in TREBAS]
        self.assertEqual(len(slugs), len(set(slugs)))


class WorshipCardsTests(TestCase):
    """Карточки «За чем к нам приходят» — единственный путь с главной к требам.

    Главная больше не показывает все семь треб по одной: шесть карточек
    группируют их и ведут на якоря. Значит, проверять надо не «каждая треба
    есть на главной», а «каждый якорь карточки существует на странице» —
    иначе читатель попадёт в начало страницы и будет искать нужное сам.
    """

    def test_card_anchors_point_at_real_trebas(self):
        slugs = {t["slug"] for t in TREBAS}
        for item in WORSHIP:
            anchor = item.get("anchor")
            if anchor:
                self.assertIn(anchor, slugs, f"якорь {anchor} не совпадает ни с одной требой")

    def test_card_anchors_exist_on_the_trebas_page(self):
        page = self.client.get(reverse("core:trebas")).content.decode()
        for item in WORSHIP:
            if item.get("anchor"):
                self.assertIn(f'id="{item["anchor"]}"', page)

    def test_home_shows_every_card(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        for item in WORSHIP:
            self.assertContains(response, str(item["title"]))
        for item in PARISH_LIFE:
            self.assertContains(response, str(item["title"]))

    def test_every_card_route_resolves(self):
        """url_name разворачивается в шаблоне: опечатка здесь — это 500 на
        главной, а не ошибка при импорте."""
        for item in tuple(WORSHIP) + tuple(PARISH_LIFE):
            self.assertTrue(reverse(item["url_name"]))


class FoundedYearTests(TestCase):
    """Год основания — единственная клетка полосы, которую нельзя выдумать."""

    def test_hidden_when_unset(self):
        home = self.client.get(reverse("core:home")).content.decode()
        self.assertNotIn("Год основания церкви", home)

    def test_shown_without_a_thousands_separator(self):
        settings = SiteSettings.get_solo()
        settings.founded_year = 1994
        settings.save()

        home = self.client.get(reverse("core:home")).content.decode()
        self.assertIn("Год основания церкви", home)
        self.assertIn("1994", home)
        # «1 994» — это то, что даёт локаль, если год пропустить как число.
        self.assertNotIn("1&nbsp;994", home)
        self.assertNotIn("1 994", home)
