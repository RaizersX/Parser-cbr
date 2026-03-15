import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import json

ua = UserAgent().random

headers = {
    'User-Agent' : ua
}
response = httpx.get(url='https://www.cbr.ru/currency_base/daily/', headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

table = soup.find('div', class_='table').find_all('tr')
data = []
for tr in table:
    try:
        data.append(tuple(tr.find('td').find_next_siblings('td')))
    except AttributeError:
        continue

date = datetime.now()
currencies = []
for cod, ed, value, curs in data:
    currencies.append({
        'Букв.код' : cod.get_text(strip=True),
        'Единица' : ed.get_text(strip=True),
        'Валюта' : value.get_text(strip=True),
        'Курс' : curs.get_text(strip=True) 
    })
result = {
    'updated' : date.strftime('%d:%m:%Y_%H:%M'),
    'currencies' : currencies
}

with open('last.json', 'w', encoding='utf-8') as file:
    json.dump(result, file, indent=2, ensure_ascii=False)

old_data = {}
with open('last.json', 'r', encoding='utf-8') as file:
    old = json.load(file)

    for item in old.get('currencies', []):
        old_data[item['Букв.код']] = float(item['Курс'].replace(',', '.'))

for item in currencies:
    code = item['Букв.код']
    new_rate = float(item['Курс'].replace(',', '.'))
    old_rate = old_data.get(code)
    
    if old_rate:
        diff = new_rate - old_rate
        sign = '▲' if diff > 0 else '▼'
        print(f"{code}: {new_rate} ₽ {sign} {abs(diff):.2f}")
    else:
        print(f"{code}: {new_rate} ₽ (нет данных за вчера)")    