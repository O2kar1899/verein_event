from django import template
from django.forms import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Custom Django Template Filter zur Hinzufügung von CSS-Klassen zu Formularfeldern.
    
    Ermöglicht das dynamische Hinzufügen von Tailwind CSS (oder anderen) Klassen 
    zu Django-Formularfeldern in Templates.
    
    Verwendung im Template:
    {{ form.field|add_class:"bg-white border rounded" }}
    
    Args:
        field (BoundField|str): Django Formularfeld oder beliebiger String
        css_class (str): CSS-Klassen als String (z.B. "w-full p-2 border")
    
    Returns:
        BoundField: Formularfeld mit hinzugefügten CSS-Klassen
        str: Unveränderter Input, falls kein Formularfeld
    
    Beispiele:
        - Basisnutzung: {{ form.username|add_class:"input-style" }}
        - Mit Tailwind: {{ form.password|add_class:"w-full p-2 border rounded" }}
    
    Wartungshinweise:
        - Filter funktioniert mit allen Django Formularfeldern
        - Existierende Klassen des Feldes bleiben erhalten
        - Bei Problemen: print(field.field.widget.attrs) zur Debugging
    """
    if isinstance(field, BoundField):
        return field.as_widget(attrs={
            "class": " ".join([field.css_classes(), css_class])
        })
    return field

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Fügt CSS-Klassen zu einem Formularfeld hinzu.
    Verwendung im Template: {{ field|add_class:"meine-klassen" }}
    """
    return field.as_widget(attrs={"class": css_class})