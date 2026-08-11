from django.shortcuts import render

from .models import RussianSchoolPage


def school_page(request):
    page = RussianSchoolPage.get_solo()
    return render(request, "school/page.html", {"page": page, "photos": page.photos.all()})
