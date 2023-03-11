from django.utils import timezone

now = timezone.now()


def year(request):
    now = timezone.now()
    return {
        "year": now.year,
    }
