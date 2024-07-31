import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

def parse_data():
    # URL страницы для парсинга
    url = 'https://abit.itmo.ru/rating/master/budget/1959'

    # Отправляем запрос и получаем HTML-контент
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Находим все элементы с нужным классом
    elements = soup.find_all(class_='RatingPage_table__item__qMY0F')

    # Инициализируем счетчики
    valid_elements_count = 0
    priority_elements = 0
    document_elements = 0

    # Проходим только по первым 215 элементам
    for element in elements[:215]:
        # Проверяем наличие нужных классов и разметки
        info_left = element.find_all(class_='RatingPage_table__infoLeft__Y_9cA')
        info = element.find_all(class_='RatingPage_table__info__quwhV')
        
        priority_valid = False
        documents_valid = False

        for info_item in info_left:
            p_tags = info_item.find_all('p')
            for p in p_tags:
                if 'Приоритет:' in p.get_text():
                    span = p.find('span')
                    if span and span.get_text(strip=True) == '1':
                        priority_valid = True

        for info_item in info:
            div_tags = info_item.find_all('div')    
            for div in div_tags:
                p_tags = div.find_all('p')
                for p in p_tags:
                    if 'Оригиналы документов:' in p.get_text():
                        span = p.find('span')
                        if span and span.get_text(strip=True) == 'да':
                            documents_valid = True

        # Если оба условия выполнены, увеличиваем счетчик валидных элементов
        if priority_valid and documents_valid:
            valid_elements_count += 1
        
        if priority_valid:
            priority_elements += 1

        if documents_valid:
            document_elements += 1

    return len(elements), priority_elements, document_elements, valid_elements_count

@app.route('/')
def index():
    total_count, priority_elements, document_elements, valid_elements_count = parse_data()
    return render_template('index.html', total_count=total_count, 
                           priority_elements=priority_elements, 
                           document_elements=document_elements, 
                           valid_elements_count=valid_elements_count)

@app.route('/refresh')
def refresh():
    total_count, priority_elements, document_elements, valid_elements_count = parse_data()
    return render_template('index.html', total_count=total_count, 
                           priority_elements=priority_elements, 
                           document_elements=document_elements, 
                           valid_elements_count=valid_elements_count)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
