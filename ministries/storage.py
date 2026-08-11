from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Ministry documents/reports/attachments live outside MEDIA_ROOT and are never
# served directly by the webserver — access goes through view functions that
# check MinistryDocument.visibility / membership before streaming the file.
private_storage = FileSystemStorage(location=str(settings.PRIVATE_MEDIA_ROOT))
