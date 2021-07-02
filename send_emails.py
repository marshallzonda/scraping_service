import os, sys
import django
import datetime
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from scraping_service.settings import EMAIL_HOST_USER

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_service.settings'

django.setup()
from scraping.models import Vacancy, Error, Url
ADMIN_USER = EMAIL_HOST_USER
today = datetime.datetime.today()
subject = f"Рассылка вакансий за {today}"
text_content = f"Рассылка вакансий за {today}"
from_email = EMAIL_HOST_USER
empty = '<h3> К сожалению на сегодня по Вашим предпочтениям данных нет. </h3>'

User = get_user_model()
qs = User.objects.filter(send_email=True).values('city', 'language', 'email')
users_dct = {}
for i in qs:
    users_dct.setdefault((i['city'], i['language']), [])
    users_dct[(i['city'], i['language'])].append(i['email'])
if users_dct:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in users_dct.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])

    qs = Vacancy.objects.filter(**params, timestamp=today).values()
    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)
    for keys, emails in users_dct.items():
        rows = vacancies.get(keys, [])
        html = ''
        for row in rows:
            html += f'<h5><a href="{row["url"]}">{ row["title"] }</a></h5>'
            html += f'<p> {row["description"]}</p>'
            html += f'<p> {row["company"]}</p><br><hr>'
        _html = html if html else empty
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(_html, "text/html")
            msg.send()

qs = Error.objects.filter(timestamp=today)
subject = ""
text_content = ''
to = ADMIN_USER
_html = ''
if qs.exists():
    error = qs.first()
    data = error.data.get('errors', [])

    for i in data:
        _html += f'<h5><a href="{i["url"]}"> Error :{ i["title"] }</a></h5>'
    subject = f'Ошибки скрапинга {today}'
    text_content = f'Ошибки скрапинга {today}'
    data = error.data.get('user_data')
    if data:
        _html += '<hr>'
        _html += '<h3>Пожелания пользователей</h3>'
        for i in data:
            _html += f'<h5>Город : {i["city"]}, Специальность: {i["language"]} Имейл: {i["email"]}</h5>'
        subject = f'Пожелания пользователей {today}'
        text_content = f'Пожелания пользователей {today}'

qs = Url.objects.all().values('city', 'language')
urls_dct = {(i['city'], i['language']): True for i in qs}
urls_errors = ''
for keys in users_dct.keys():
    if keys not in urls_dct:
        if keys[0] and keys[0]:
            urls_errors += f'<p>Для города:{keys[0]}  и ЯП: { keys[1] } отсутствуют урлы<p><br>'

if urls_errors:
    subject += 'Отсутсвующие урлы'
    _html = urls_errors

if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()