from django import template

register = template.Library()

register.simple_tag(name='is_registered')

@register.simple_tag(name='is_registered', takes_context=True)
def is_registered(context, value):
    try:
        request = context['request']
        if value.is_registered(request.user):
            return True
        else:
            return False
    except:
        return False


