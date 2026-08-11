from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import RussianSchoolPage


class SeedParishSchoolTests(TestCase):
    """seed_parish must fill the Russian school page and never clobber edits."""

    def test_seed_fills_description_and_tuition_note(self):
        call_command("seed_parish")
        page = RussianSchoolPage.get_solo()
        self.assertTrue(page.description_ru)
        self.assertTrue(page.description_en)
        self.assertTrue(page.tuition_note_ru)
        self.assertTrue(page.tuition_note_en)

    def test_seed_does_not_overwrite_existing_description(self):
        page = RussianSchoolPage.get_solo()
        page.description = "Уже написано настоятелем."
        page.save()

        call_command("seed_parish")

        page.refresh_from_db()
        self.assertEqual(page.description, "Уже написано настоятелем.")


class RussianSchoolPageViewTests(TestCase):
    def test_page_renders_seeded_content(self):
        call_command("seed_parish")
        response = self.client.get(reverse("school:page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Русская школа")
