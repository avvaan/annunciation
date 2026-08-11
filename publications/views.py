from django.shortcuts import render

from .models import Publication


def publication_list(request):
    calendars = Publication.objects.filter(is_published=True, kind=Publication.Kind.CALENDAR)
    bulletins = Publication.objects.filter(is_published=True, kind=Publication.Kind.BULLETIN)
    return render(request, "publications/list.html", {"calendars": calendars, "bulletins": bulletins})
