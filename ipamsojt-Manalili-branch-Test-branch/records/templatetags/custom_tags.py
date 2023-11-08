from django import template

register = template.Library()

@register.filter
def has_match(recorduploads, upload_pk):
    return any(record.upload.pk == upload_pk for record in recorduploads)