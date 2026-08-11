from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import PageText

register = template.Library()


class EditableNode(template.Node):
    def __init__(self, page, block, label, nodelist):
        self.page = page
        self.block = block
        self.label = label
        self.nodelist = nodelist

    def render(self, context):
        page = self.page.resolve(context)
        block = self.block.resolve(context)
        label = self.label.resolve(context) if self.label else ""
        default_text = self.nodelist.render(context)

        obj, created = PageText.objects.get_or_create(
            page=page, block=block,
            defaults={"label": label, "body_ru": default_text.strip()},
        )
        body = obj.body or default_text

        request = context.get("request")
        if request and request.user.is_authenticated and request.user.is_staff:
            edit_url = reverse("admin:core_pagetext_change", args=[obj.pk])
            return mark_safe(
                f'<div class="editable-block" data-editable="{page}:{block}">'
                f'{body}'
                f'<a class="editable-block__edit" href="{edit_url}" '
                f'title="Редактировать в админке">✎</a></div>'
            )
        return mark_safe(body)


def do_editable(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "{% editable %} требует минимум 'page' и 'block': "
            "{% editable 'history' 'intro' 'Вступление' %}...{% endeditable %}"
        )
    page = parser.compile_filter(bits[1])
    block = parser.compile_filter(bits[2])
    label = parser.compile_filter(bits[3]) if len(bits) > 3 else None
    nodelist = parser.parse(("endeditable",))
    parser.delete_first_token()
    return EditableNode(page, block, label, nodelist)


register.tag("editable", do_editable)
