"""Тег для снимков прихода с готовыми узкими вариантами.

Телефон качал полноразмерный десктопный файл: главная весила 1,55 МБ, из
них 1,18 МБ — четыре JPEG, каждый впятеро крупнее места, куда он вставал.
Для снимков, лежащих в репозитории, рядом собраны варианты на 480 и 960
пикселей, и браузер сам берёт подходящий.

Снимок, загруженный секретарём через админку, отдаётся как есть: обрезать
его на лету нечем, а тихо подсовывать несуществующий вариант хуже, чем
отдать оригинал. Здесь это видно в одном месте, а не размазано по семи
шаблонам.
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

VARIANT_WIDTHS = (480, 960)


@register.simple_tag
def parish_photo(uploaded, default_stem, *, sizes="100vw", alt="", css_class="", eager=False):
    """<img> со снимком: загруженным из админки или встроенным по умолчанию."""
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'

    if uploaded:
        return format_html(
            '<img src="{}" alt="{}" class="{}" {}>',
            uploaded.url, alt, css_class, mark_safe(loading),
        )

    base = f"/static/images/photos/{default_stem}"
    srcset = ", ".join(f"{base}-{w}.jpg {w}w" for w in VARIANT_WIDTHS)
    srcset += f", {base}.jpg 1600w"
    return format_html(
        '<img src="{}.jpg" srcset="{}" sizes="{}" alt="{}" class="{}" {}>',
        base, srcset, sizes, alt, css_class, mark_safe(loading),
    )
