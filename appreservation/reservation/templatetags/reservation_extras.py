from django import template

register = template.Library()

# Tag filtro que mutiplica el precio de la habitacio
# por los dias y si es el mismo dia devuelve solo
# el precio de la habitacion
@register.filter
def mul(value, arg):
    if arg == 0:
        return value
    else:
        return value * arg