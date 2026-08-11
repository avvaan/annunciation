from django.core.management.base import BaseCommand

from core.models import DonationMethod, DonationPage, FirstVisitPage, SiteSettings
from school.models import RussianSchoolPage
from services.models import ServiceType


class Command(BaseCommand):
    """Fill a fresh install with the parish's own details and starter copy.

    Safe to re-run: it only writes a field that is still empty, so nothing the
    secretary has already edited in the admin is ever overwritten. Pass
    --force to overwrite regardless.
    """

    help = "Наполнить свежую установку данными прихода (адрес, контакты, стартовые тексты)."

    # The parish's factual details.
    PARISH = {
        "parish_name": "Приход Благовещения Пресвятой Богородицы",
        "city": "Джексонвиль, Флорида",
        "address": "9795 Old St. Augustine Road, Jacksonville, FL 32257",
        "phone": "(904) 361-3445",
        "email": "aocjax@gmail.com",
        "hero_lede": "Русскоязычный православный приход в Джексонвилле. "
                     "Богослужения совершаются на церковнославянском, часть — по-английски.",
    }

    FIRST_VISIT = {
        "when_text": "Часы и Литургия — по воскресеньям в 9:30 утра.",
        "intro": (
            "Мы русскоязычный православный приход в Джексонвилле. Если вы никогда "
            "не были на православной службе — приходите: знать заранее ничего "
            "не нужно, и никто не будет смотреть на вас с осуждением."
        ),
        "what_to_expect": (
            "Служба идёт около двух часов, в основном на церковнославянском языке, "
            "часть — по-английски. У входа лежат бюллетени на двух языках. "
            "После Литургии все остаются на общую трапезу — оставайтесь и вы, "
            "это лучший способ познакомиться с приходом."
        ),
        "practical": (
            "Парковка бесплатная. Особых требований к одежде нет — приходите в том, "
            "в чём вам удобно. У свечного ящика всегда есть кто-то, кто подскажет, "
            "куда идти и что сейчас происходит."
        ),
        "communion_note": (
            "К Причастию в православной церкви приступают крещёные православные "
            "христиане, подготовившись молитвой, постом и исповедью. Если вы давно "
            "не исповедовались или только присматриваетесь к вере — просто подойдите "
            "к священнику, он всё объяснит."
        ),
    }

    SERVICE_TYPES = [
        ("Всенощное бдение", 0),
        ("Утреня", 1),
        ("Часы", 2),
        ("Исповедь", 3),
        ("Литургия", 4),
        ("Вечерня", 5),
        ("Акафист", 6),
        ("Молебен", 7),
        ("Панихида", 8),
        ("Трапеза", 9),
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

        created = 0
        for name, order in self.SERVICE_TYPES:
            _, was_created = ServiceType.objects.get_or_create(name=name, defaults={"order": order})
            created += was_created
        if created:
            self.stdout.write(f"Типы служб: добавлено {created}.")

        school = RussianSchoolPage.get_solo()
        self._fill(school, {
            "schedule_text": "По понедельникам и вторникам, с 16:00 до 20:00, один раз в неделю.",
            "contact_email": "aocrussianschool@gmail.com",
        }, force, "Русская школа")

        donation = DonationPage.get_solo()
        self._fill(donation, {
            "intro": "Приход не получает финансирования извне. Содержание храма, "
                     "богослужение и все приходские дела оплачиваются приношением прихожан.",
        }, force, "Пожертвования")
        if not donation.methods.exists():
            DonationMethod.objects.create(
                page=donation, order=1, title="Онлайн",
                description="Разовое или регулярное пожертвование банковской картой.",
                button_label="Пожертвовать",
            )
            DonationMethod.objects.create(
                page=donation, order=2, title="Чек по почте",
                description="Выписать на Annunciation Orthodox Church "
                            "и отправить по адресу прихода.",
            )
            self.stdout.write("Способы пожертвования: добавлены заготовки.")

        self.stdout.write(self.style.SUCCESS(
            "Готово. Всё это правится в админке — команда ничего не перезапишет "
            "при повторном запуске."
        ))

    def _fill(self, obj, values, force, label):
        """Write only the fields still empty, unless --force."""
        touched = []
        for field, value in values.items():
            if force or not getattr(obj, field, None):
                setattr(obj, field, value)
                touched.append(field)
        if touched:
            obj.save()
            self.stdout.write(f"{label}: заполнено {len(touched)} пол(я).")
        else:
            self.stdout.write(f"{label}: уже заполнено, пропущено.")
