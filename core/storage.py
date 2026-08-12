from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateMediaStorage(FileSystemStorage):
    """Файлы вне MEDIA_ROOT — их не отдаёт веб-сервер, только вьюха с проверкой прав.

    Путь читается из настроек при каждом обращении, а не в конструкторе.
    Иначе абсолютный путь машины, на которой запустили makemigrations,
    вмерзает в файл миграции: на Render каталог другой (он приходит из
    RENDER_DISK_MOUNT_PATH), и тесты не могут увести хранилище во
    временную папку. По той же причине deconstruct() отдаёт пустой список
    аргументов — в миграции остаётся один только класс.
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("location", None)
        super().__init__(*args, **kwargs)

    @property
    def base_location(self):
        return str(settings.PRIVATE_MEDIA_ROOT)

    @property
    def location(self):
        return str(settings.PRIVATE_MEDIA_ROOT)


private_storage = PrivateMediaStorage()
