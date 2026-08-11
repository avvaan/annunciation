from django.core.management.base import BaseCommand

from building.models import BuildingProject
from core.models import (
    DonationMethod,
    DonationPage,
    FirstVisitPage,
    PageText,
    SiteSettings,
)
from school.models import RussianSchoolPage
from services.models import ServiceType


class Command(BaseCommand):
    """Fill a fresh install with the parish's own details and starter copy.

    Writes both languages: modeltranslation keeps a `_ru` and an `_en` column
    per translated field, and an empty `_en` silently falls back to Russian —
    which is what made the English site read half-Russian before.

    Safe to re-run: only fields that are still empty get written, so nothing the
    secretary has already edited in the admin is overwritten. Use --force to
    overwrite regardless.
    """

    help = "Наполнить свежую установку данными прихода (адрес, контакты, стартовые тексты, RU + EN)."

    # Factual details — same in both languages except the parish's own name.
    PARISH = {
        "parish_name": (
            "Приход Благовещения Пресвятой Богородицы",
            "Annunciation Orthodox Church",
        ),
        "city": ("Джексонвиль, Флорида", "Jacksonville, Florida"),
        "address": ("9795 Old St. Augustine Road, Jacksonville, FL 32257",) * 2,
        "phone": ("(904) 361-3445",) * 2,
        "email": ("aocjax@gmail.com",) * 2,
        "hero_lede": (
            "Русскоязычный православный приход в Джексонвилле. Богослужения "
            "совершаются на церковнославянском, часть — по-английски.",
            "A Russian-speaking Orthodox parish in Jacksonville. Services are served "
            "in Church Slavonic, with parts in English.",
        ),
    }

    FIRST_VISIT = {
        "when_text": (
            "Часы и Литургия — по воскресеньям в 9:30 утра.",
            "Hours and Divine Liturgy — Sundays at 9:30 am.",
        ),
        "intro": (
            "Мы русскоязычный православный приход в Джексонвилле. Если вы никогда "
            "не были на православной службе — приходите: знать заранее ничего "
            "не нужно, и никто не будет смотреть на вас с осуждением.",
            "We are a Russian-speaking Orthodox parish in Jacksonville. If you have "
            "never been to an Orthodox service, simply come: nothing needs to be known "
            "in advance, and no one will look at you askance.",
        ),
        "what_to_expect": (
            "Служба идёт около двух часов, в основном на церковнославянском языке, "
            "часть — по-английски. У входа лежат бюллетени на двух языках. "
            "После Литургии все остаются на общую трапезу — оставайтесь и вы, "
            "это лучший способ познакомиться с приходом.",
            "The service lasts about two hours, mostly in Church Slavonic, with parts "
            "in English. Bulletins in both languages are by the entrance. After the "
            "Liturgy everyone stays for a shared meal — please stay too; it is the best "
            "way to get to know the parish.",
        ),
        "practical": (
            "Парковка бесплатная. Особых требований к одежде нет — приходите в том, "
            "в чём вам удобно. У свечного ящика всегда есть кто-то, кто подскажет, "
            "куда идти и что сейчас происходит.",
            "Parking is free. There is no dress code — come in whatever you are "
            "comfortable in. Someone is always at the candle desk who can tell you "
            "where to go and what is happening.",
        ),
        "communion_note": (
            "К Причастию в православной церкви приступают крещёные православные "
            "христиане, подготовившись молитвой, постом и исповедью. Если вы давно "
            "не исповедовались или только присматриваетесь к вере — просто подойдите "
            "к священнику, он всё объяснит.",
            "In the Orthodox Church, Communion is received by baptised Orthodox "
            "Christians who have prepared through prayer, fasting and confession. "
            "If it has been a long time since your last confession, or you are only "
            "beginning to look into the faith, simply speak to the priest — he will "
            "explain everything.",
        ),
    }

    BUILDING = {
        "title": ("Строительство храма", "Building the church"),
    }

    SCHOOL = {
        "description": (
            "Русская школа при нашем приходе — это место, где дети растут в родном "
            "языке, культуре и вере одновременно. Мы читаем и пишем по-русски, "
            "разбираем сказки и историю, готовимся к православным праздникам и "
            "поём вместе перед Пасхой и Рождеством.\n\n"
            "Занятия ведут прихожане-волонтёры для детей разных возрастов — от "
            "первых букв до свободного чтения. Приходите познакомиться на любое "
            "занятие, запись открыта в течение учебного года.",
            "The Russian School at our parish is where children grow up in their "
            "native language, culture and faith together. We read and write in "
            "Russian, explore folk tales and history, prepare for Orthodox feasts "
            "and sing together before Pascha and Christmas.\n\n"
            "Classes are taught by parish volunteers for children of different "
            "ages, from first letters to fluent reading. Come by any class to see "
            "how it works — enrollment stays open through the school year.",
        ),
        "schedule_text": (
            "По понедельникам и вторникам, с 16:00 до 20:00, один раз в неделю.",
            "Mondays and Tuesdays, 4 pm to 8 pm, once a week.",
        ),
        "tuition_note": (
            "Точную сумму и способы оплаты уточняйте у координатора школы.",
            "Ask the school coordinator for the current tuition amount and how to pay.",
        ),
    }

    DONATION = {
        "intro": (
            "Приход не получает финансирования извне. Содержание храма, богослужение "
            "и все приходские дела оплачиваются приношением прихожан.",
            "The parish receives no outside funding. The upkeep of the church, the "
            "services and everything the parish does are paid for by the offerings "
            "of its people.",
        ),
    }

    DONATION_METHODS = [
        {
            "order": 1,
            "title": ("Онлайн", "Online"),
            "description": (
                "Разовое или регулярное пожертвование банковской картой.",
                "A one-off or recurring gift by bank card.",
            ),
            "button_label": ("Пожертвовать", "Give"),
        },
        {
            "order": 2,
            "title": ("Чек по почте", "Cheque by post"),
            "description": (
                "Выписать на Annunciation Orthodox Church и отправить по адресу прихода.",
                "Make it out to Annunciation Orthodox Church and post it to the parish address.",
            ),
            "button_label": ("", ""),
        },
    ]

    # Blocks the {% editable %} tag would otherwise seed from the templates'
    # Russian defaults alone, leaving the English pages reading Russian.
    PAGE_TEXTS = [
        {
            "page": "about", "block": "intro", "label": "Вступление",
            "ru": "<p>Наш приход объединяет русскоязычных православных христиан "
                  "Джексонвилла и окрестностей.</p>",
            "en": "<p>Our parish gathers Russian-speaking Orthodox Christians of "
                  "Jacksonville and the surrounding area.</p>",
        },
        {
            "page": "history", "block": "intro", "label": "Вступление",
            "ru": "<p>История нашего прихода — это история русской православной "
                  "общины Джексонвилла.</p>",
            "en": "<p>The history of our parish is the history of the Russian "
                  "Orthodox community of Jacksonville.</p>",
        },
    ]

    SERVICE_TYPES = [
        ("Всенощное бдение", "All-Night Vigil", 0),
        ("Утреня", "Matins", 1),
        ("Часы", "Hours", 2),
        ("Исповедь", "Confession", 3),
        ("Литургия", "Divine Liturgy", 4),
        ("Вечерня", "Vespers", 5),
        ("Акафист", "Akathist", 6),
        ("Молебен", "Moleben", 7),
        ("Панихида", "Panikhida", 8),
        ("Трапеза", "Shared meal", 9),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Перезаписать поля, даже если они уже заполнены.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        self._fill(SiteSettings.get_solo(), self.PARISH, force, "Настройки сайта")
        self._fill(FirstVisitPage.get_solo(), self.FIRST_VISIT, force, "«Впервые здесь?»")
        self._fill(RussianSchoolPage.get_solo(), self.SCHOOL, force, "Русская школа")
        self._fill(BuildingProject.get_solo(), self.BUILDING, force, "Строительный проект")

        school = RussianSchoolPage.get_solo()
        if force or not school.contact_email:
            school.contact_email = "aocrussianschool@gmail.com"
            school.save()

        created = 0
        for ru, en, order in self.SERVICE_TYPES:
            obj, was_created = ServiceType.objects.get_or_create(
                name_ru=ru, defaults={"name": ru, "order": order}
            )
            if force or not obj.name_en:
                obj.name_en = en
                obj.save()
            created += was_created
        if created:
            self.stdout.write(f"Типы служб: добавлено {created}.")

        for spec in self.PAGE_TEXTS:
            block, was_created = PageText.objects.get_or_create(
                page=spec["page"], block=spec["block"],
                defaults={"label": spec["label"], "body_ru": spec["ru"], "body_en": spec["en"]},
            )
            if not was_created and (force or not block.body_en or block.body_en == block.body_ru):
                block.body_en = spec["en"]
                if force or not block.body_ru:
                    block.body_ru = spec["ru"]
                block.save()
        self.stdout.write(f"Редактируемые блоки: проверено {len(self.PAGE_TEXTS)}.")

        donation = DonationPage.get_solo()
        self._fill(donation, self.DONATION, force, "Пожертвования")
        if not donation.methods.exists():
            for spec in self.DONATION_METHODS:
                method = DonationMethod(page=donation, order=spec["order"])
                for field in ("title", "description", "button_label"):
                    ru, en = spec[field]
                    setattr(method, f"{field}_ru", ru)
                    setattr(method, f"{field}_en", en)
                    setattr(method, field, ru)
                method.save()
            self.stdout.write("Способы пожертвования: добавлены заготовки (RU + EN).")

        self.stdout.write(self.style.SUCCESS(
            "Готово. Всё это правится в админке — команда ничего не перезапишет "
            "при повторном запуске."
        ))

    def _fill(self, obj, values, force, label):
        """Write the `_ru` and `_en` column of each field that is still unset.

        "Unset" is not simply "empty": a model `default=` is copied into every
        language column by modeltranslation, so an English column can arrive
        already holding the Russian default. An English value that merely
        mirrors the Russian one has not been translated, so it counts as unset.
        """
        touched = []
        for field, (ru, en) in values.items():
            ru_field, en_field = f"{field}_ru", f"{field}_en"

            if not hasattr(obj, ru_field):        # field is not translated at all
                if force or not getattr(obj, field, None):
                    setattr(obj, field, ru)
                    touched.append(field)
                continue

            if force or not getattr(obj, ru_field, None):
                setattr(obj, ru_field, ru)
                touched.append(ru_field)

            current_en = getattr(obj, en_field, None)
            # Only treat "mirrors the Russian" as untranslated when this seed
            # actually carries a distinct English string. Where the two are
            # legitimately identical (address, phone, email), a mirrored value
            # is correct — and rewriting it every run would clobber an edit the
            # secretary made in both languages at once.
            untranslated = not current_en or (
                en != ru and current_en == getattr(obj, ru_field, None)
            )
            if force or untranslated:
                setattr(obj, en_field, en)
                touched.append(en_field)

            # keep the bare accessor in step with the source language
            if force or not getattr(obj, field, None):
                setattr(obj, field, ru)

        if touched:
            obj.save()
            self.stdout.write(f"{label}: заполнено {len(touched)} пол(я).")
        else:
            self.stdout.write(f"{label}: уже заполнено, пропущено.")
