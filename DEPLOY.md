# Развёртывание на Render

## Настройки веб-сервиса

| Поле | Значение |
|---|---|
| Language | Python 3 |
| Branch | `main` |
| Root Directory | оставить пустым |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python manage.py seed_parish` |
| Start Command | `gunicorn annunciation.wsgi:application` |
| Instance Type | Free — для проверки; на рабочем сайте платный (Free засыпает) |

`collectstatic`, `migrate` и `seed_parish` стоят в Build Command: у Render нет
отдельной фазы release, для Django это стандартный приём.

`seed_parish` заполняет свежую установку данными прихода — адрес, телефон,
почта, типы служб, стартовые тексты «Впервые здесь?» и пожертвований.
Команда **идемпотентна**: при повторном запуске она трогает только пустые поля,
поэтому всё, что секретарь уже поправила в админке, остаётся как есть.
Перезаписать принудительно — `python manage.py seed_parish --force`.

## Переменные окружения

| Ключ | Значение |
|---|---|
| `SECRET_KEY` | случайный (в Render есть кнопка Generate) |
| `DJANGO_DEBUG` | `0` |
| `PYTHON_VERSION` | `3.11.15` |
| `ALLOWED_HOSTS` | можно не задавать — хост `*.onrender.com` подхватывается сам через `RENDER_EXTERNAL_HOSTNAME` |
| `RENDER_DISK_MOUNT_PATH` | путь монтирования диска, например `/var/data` — см. ниже |

## Обязательно после создания сервиса

1. **PostgreSQL.** Без `DATABASE_URL` сайт пишет в SQLite на эфемерный диск, и
   база стирается при каждом деплое. Создать на Render PostgreSQL и подключить
   к сервису — Render сам пропишет `DATABASE_URL`.
2. **Диск для загруженных файлов.** PDF расписаний, документы служений и фото
   тоже лежат на эфемерном диске. Добавить Render Disk (Settings → Disks) и
   задать `RENDER_DISK_MOUNT_PATH` — `MEDIA_ROOT` и `PRIVATE_MEDIA_ROOT`
   переедут туда автоматически. Без диска сайт работает, но загруженные файлы
   пропадают при передеплое.
3. **Суперпользователь.** Через вкладку Shell у сервиса:
   `python manage.py createsuperuser`
4. **Группа «Секретарь»** — для повседневного редактирования без полного
   доступа к админке: `python manage.py create_secretary_group`

## Что заполнить в админке после запуска

- **Настройки сайта** → фото на первый экран, ссылки Realm.
- **Духовенство** → карточки с портретами.
- **Расписание богослужений** → правила повторяющихся служб, затем действие
  «сгенерировать на 4/8 недель вперёд» и точечная правка под праздники.
- **История прихода**, **Строительный проект**, **Русская школа** → тексты и фото.
