"""Проверки записок: приём формы, отсев ботов и круг сорокоуста."""

import shutil
import tempfile
import time

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import CommemorationForm
from .models import Commemoration, CommemorationBatch
from .pdf import render_batch_pdf


def payload(**overrides):
    data = {
        "kind": Commemoration.Kind.LITURGY,
        "requester_name": "Анна",
        "email": "anna@example.com",
        "phone": "",
        "living_names": "Марии\nИоанна",
        "departed_names": "мл. Николая",
        "notes": "",
        "website": "",
        "form_timestamp": str(time.time() - 30),
    }
    data.update(overrides)
    return data


class SubmitFormTests(TestCase):
    def test_accepts_a_normal_note(self):
        response = self.client.post(reverse("commemorations:submit"), payload())
        note = Commemoration.objects.get()
        self.assertRedirects(
            response, reverse("commemorations:accepted", args=[note.pk])
        )
        self.assertEqual(note.living_list, ["Марии", "Иоанна"])
        self.assertEqual(note.departed_list, ["мл. Николая"])
        self.assertEqual(note.total_liturgies, 1)

    def test_names_typed_through_commas_become_one_per_line(self):
        form = CommemorationForm(payload(living_names="Марии, Иоанна; Александра"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["living_names"], "Марии\nИоанна\nАлександра")

    def test_note_without_a_single_name_is_refused(self):
        form = CommemorationForm(payload(living_names="", departed_names=""))
        self.assertFalse(form.is_valid())
        self.assertIn("хотя бы одно имя", str(form.errors))

    def test_note_without_any_contact_is_refused(self):
        form = CommemorationForm(payload(email="", phone=""))
        self.assertFalse(form.is_valid())
        self.assertIn("телефон", str(form.errors))

    def test_filled_honeypot_is_refused(self):
        form = CommemorationForm(payload(website="http://spam.example"))
        self.assertFalse(form.is_valid())
        self.assertEqual(Commemoration.objects.count(), 0)

    def test_instant_submission_is_refused(self):
        form = CommemorationForm(payload(form_timestamp=str(time.time())))
        self.assertFalse(form.is_valid())

    def test_overlong_list_is_refused(self):
        form = CommemorationForm(payload(living_names="\n".join(["Иоанна"] * 200)))
        self.assertFalse(form.is_valid())
        self.assertIn("Не больше", str(form.errors))

    def test_sorokoust_gets_forty_liturgies(self):
        self.client.post(
            reverse("commemorations:submit"),
            payload(kind=Commemoration.Kind.SOROKOUST),
        )
        note = Commemoration.objects.get()
        self.assertEqual(note.total_liturgies, Commemoration.SOROKOUST_LITURGIES)
        self.assertEqual(note.remaining_liturgies, Commemoration.SOROKOUST_LITURGIES)


class TempPrivateMedia:
    """PDF пишется на диск по-настоящему, поэтому уводим приватное
    хранилище во временный каталог — иначе тесты сорят в рабочей папке."""

    @classmethod
    def setUpClass(cls):
        cls._media_dir = tempfile.mkdtemp()
        cls._override = override_settings(PRIVATE_MEDIA_ROOT=cls._media_dir)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._media_dir, ignore_errors=True)


class PrintingTests(TempPrivateMedia, TestCase):
    def setUp(self):
        self.single = Commemoration.objects.create(
            requester_name="Пётр", living_names="Марии", departed_names="Иоанна"
        )
        self.sorokoust = Commemoration.objects.create(
            kind=Commemoration.Kind.SOROKOUST,
            requester_name="Ольга",
            departed_names="Николая\nЕлены",
        )

    def _collect_and_print(self):
        batch = CommemorationBatch.objects.create(title="Проба")
        for note in Commemoration.objects.all():
            if note.is_active:
                note.batches.add(batch)
        render_batch_pdf(batch)
        for note in batch.notes.all():
            note.mark_printed()
        return batch

    def test_pdf_is_produced_and_holds_the_names(self):
        batch = self._collect_and_print()
        batch.refresh_from_db()
        self.assertTrue(batch.pdf_file)
        self.assertEqual(batch.status, CommemorationBatch.Status.PDF_READY)
        with batch.pdf_file.open("rb") as handle:
            head = handle.read(5)
        self.assertEqual(head, b"%PDF-")

    def test_single_note_closes_after_one_printing(self):
        self._collect_and_print()
        self.single.refresh_from_db()
        self.assertEqual(self.single.status, Commemoration.Status.COMPLETED)
        self.assertFalse(self.single.is_active)

    def test_sorokoust_returns_to_the_queue_until_forty(self):
        self._collect_and_print()
        self.sorokoust.refresh_from_db()
        self.assertEqual(self.sorokoust.printed_count, 1)
        self.assertEqual(self.sorokoust.status, Commemoration.Status.PENDING)
        self.assertTrue(self.sorokoust.is_active)

        for _ in range(Commemoration.SOROKOUST_LITURGIES - 1):
            self._collect_and_print()

        self.sorokoust.refresh_from_db()
        self.assertEqual(self.sorokoust.printed_count, 40)
        self.assertEqual(self.sorokoust.remaining_liturgies, 0)
        self.assertEqual(self.sorokoust.status, Commemoration.Status.COMPLETED)
        self.assertIsNotNone(self.sorokoust.completed_at)

    def test_every_batch_keeps_its_own_note_list(self):
        first = self._collect_and_print()
        second = self._collect_and_print()
        # разовая записка закрылась после первой пачки, сорокоуст — в обеих
        self.assertIn(self.single, first.notes.all())
        self.assertNotIn(self.single, second.notes.all())
        self.assertIn(self.sorokoust, first.notes.all())
        self.assertIn(self.sorokoust, second.notes.all())


class AcceptedPageTests(TestCase):
    """Подтверждение показывает имена — значит, чужую записку по номеру
    открыть быть не должно."""

    def test_shows_the_names_that_were_submitted(self):
        self.client.post(reverse("commemorations:submit"), payload())
        note = Commemoration.objects.get()
        page = self.client.get(reverse("commemorations:accepted", args=[note.pk]))
        self.assertEqual(page.status_code, 200)
        body = page.content.decode()
        self.assertIn("Марии", body)
        self.assertIn("мл. Николая", body)

    def test_someone_elses_note_is_not_readable_by_number(self):
        self.client.post(reverse("commemorations:submit"), payload())
        note = Commemoration.objects.get()
        other = self.client.__class__()          # чистая сессия, как у чужого
        self.assertEqual(
            other.get(reverse("commemorations:accepted", args=[note.pk])).status_code,
            404,
        )


class BatchDownloadTests(TempPrivateMedia, TestCase):
    def setUp(self):
        note = Commemoration.objects.create(requester_name="Пётр", living_names="Марии")
        self.batch = CommemorationBatch.objects.create(title="Проба")
        note.batches.add(self.batch)
        render_batch_pdf(self.batch)
        self.url = reverse("commemorations:batch_pdf", args=[self.batch.pk])

    def test_anonymous_visitor_cannot_reach_the_pdf(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_ordinary_account_cannot_reach_the_pdf(self):
        get_user_model().objects.create_user("gost", password="x")
        self.client.login(username="gost", password="x")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_staff_downloads_the_pdf(self):
        get_user_model().objects.create_user("sekretar", password="x", is_staff=True)
        self.client.login(username="sekretar", password="x")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
