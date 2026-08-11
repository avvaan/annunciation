from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Council protocols, financial reports and meeting files live outside
# MEDIA_ROOT and are never served by the webserver directly — every download
# goes through a view that checks portal membership first.
council_storage = FileSystemStorage(location=str(settings.PRIVATE_MEDIA_ROOT))
