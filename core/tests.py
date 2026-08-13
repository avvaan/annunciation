"""Проверки страницы треб и её карточек на главной."""

from django.test import TestCase
from django.urls import reverse

from .trebas import TREBAS


class TrebasPageTests(TestCase):
    def test_page_lists_every_treba(self):
        response = self.client.get(reverse("core:trebas"))
        self.assertEqual(response.status_code, 200)
        for treba in TREBAS:
            self.assertContains(response, str(treba["title"]))

    def test_every_card_anchor_exists_on_the_page(self):
        """Карточка на главной ведёт на якорь; если slug разойдётся с id,
        читатель попадёт в начало страницы и будет искать нужное сам."""
        page = self.client.get(reverse("core:trebas")).content.decode()
        home = self.client.get(reverse("core:home")).content.decode()

        for treba in TREBAS:
            slug = treba["slug"]
            self.assertIn(f'id="{slug}"', page, f"нет якоря для {slug}")
            self.assertIn(f'#{slug}"', home, f"нет карточки на {slug}")

    def test_home_shows_the_cards(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        for treba in TREBAS:
            self.assertContains(response, str(treba["blurb"]))

    def test_slugs_are_unique(self):
        """Slug — и адрес якоря, и ключ правленого текста в PageText:
        совпадение молча склеило бы два описания в одно."""
        slugs = [t["slug"] for t in TREBAS]
        self.assertEqual(len(slugs), len(set(slugs)))
