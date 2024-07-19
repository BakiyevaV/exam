from django import template
from datetime import datetime
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()

@register.filter(name='custom_timesince')
def custom_timesince(value):
    now = datetime.now(value.tzinfo)
    delta = now - value

    days = delta.days
    if days == 0:
        return "сегодня"
    else:
        return f"{days} д. назад"
    
    
@register.filter(name='truncate_more')
def truncate_more(value, char_limit):
    if len(value) > char_limit:
        return mark_safe(value[:char_limit] + f'... <a class="show_detail">Подробнее</a>')
    else:
        return value

@register.filter
def get_item(dictionary, key):
    print('dictionary', dictionary)
    print('key', key)
    return dictionary.get(key)





@register.simple_tag(takes_context=True)
def paginate(context):
    page_obj = context.get('page_obj')
    if not page_obj:
        page_obj = context.get('articles')
    print('page_obj', page_obj)

    if not page_obj:
        return format_html('<div class="pagination"><div class="step-links"><div class="page current"><span>0</span></div></div></div>')

    html = '<div class="pagination"><div class="step-links">'

    if hasattr(page_obj, 'has_previous') and page_obj.has_previous():
        html += f'<a href="?page={page_obj.previous_page_number()}">предыдущая</a>'
        print('has_previous')

    if hasattr(page_obj, 'paginator'):
        print('paginator')
        for num in page_obj.paginator.page_range:
            print(num)
            if num == page_obj.number:
                html += f'<div class="page current"><span>{num}</span></div>'
            else:
                html += f'<div class="page"><a href="?page={num}">{num}</a></div>'

    if hasattr(page_obj, 'has_next') and page_obj.has_next():
        print('has_next')
        html += f'<a href="?page={page_obj.next_page_number()}">следующая</a>'

    html += '</div></div>'
    return format_html(html)