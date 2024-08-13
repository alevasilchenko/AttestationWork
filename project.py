import os
import csv
import json

DIRECTORY_OF_PRICES = ''  # по умолчанию задан каталог проекта; можно указать другой, например, 'prices'
SEARCH_STR = 'price'  # ключевой фрагмент наименования файла с прайс-листом
SEPARATOR = ';'  # по ТЗ - разделителем в файлах даных является точка с запятой, однако, по факту в приложенных файлах
# используется запятая; было принято решение определять разделитель для каждого файла данных с помощью диалекта
KEY_WORDS_FOR_PRODUCT = ('товар', 'название', 'наименование', 'продукт')  # вариации колонки "Название"
KEY_WORDS_FOR_PRICE = ('розница', 'цена')  # вариации колонки "Цена"
KEY_WORDS_FOR_WEIGHT = ('вес', 'масса', 'фасовка')  # вариации колонки "Фасовка"
TITLES_OF_HTML = ('Номер', 'Название', 'Цена', 'Фасовка', 'Файл', 'Цена за кг')

text_file_name = 'text_data.txt'  # текстовый файл с неупорядоченным списком словарей исходных данных
json_file_name = 'json_data.json'  # JSON-файл, отображающий упорядоченную по возрастанию цены за килограмм структуру


class PriceMachine:

    def __init__(self):
        self.data = []  # используется для наполнения массива неупорядоченных данных по мере сканирования файлов данных
        self.result = ''  # используется для формирования ответа на поисковый запрос в консоли
        self.name_length = 0  # используется для определения ширины колонки под наименование продукции в консоли

    def load_prices(self, file_path=DIRECTORY_OF_PRICES):

        if not file_path:
            file_path = os.getcwd()  # если не конкретизирован каталог файлов данных, используется каталог проекта

        all_list = os.listdir(file_path)

        # получаем список файлов, в наименовании которых имеется ключевое слово
        price_files = [file for file in all_list
                       if os.path.isfile(os.path.join(file_path, file)) and SEARCH_STR in file.lower()]

        for file in price_files:
            print(f'Обработка файла {file}...')
            filename = os.path.join(file_path, file)

            with open(file=filename, mode='rb') as csv_file:
                dialect = csv.Sniffer().sniff(str(csv_file.readline()), [',', ' ', ';'])  # определяем диалект

            with open(file=filename, mode='r', newline='', encoding='utf-8') as csv_file:
                csv_data = csv.DictReader(csv_file, delimiter=str(dialect.delimiter), skipinitialspace=True)
                data_pos = self.search_product_price_weigth(csv_data.fieldnames)  # находим позиции колонок по заголовку

                for row in csv_data:
                    row_product = row[list(row)[data_pos[0]]].rstrip()
                    row_price = float(row[list(row)[data_pos[1]]])
                    row_weight = float(row[list(row)[data_pos[2]]])
                    row_file = file
                    row_cost = row_price / row_weight
                    data_line = {TITLES_OF_HTML[1]: row_product.lower(),
                                 TITLES_OF_HTML[2]: round(row_price),
                                 TITLES_OF_HTML[3]: round(row_weight),
                                 TITLES_OF_HTML[4]: row_file,
                                 TITLES_OF_HTML[5]: round(row_cost, 2)}
                    self.data.append(data_line)

        with open(file=text_file_name, mode='w', encoding='utf-8') as array_data_file:
            array_data_file.write(str(self.data))  # сохраняем текстовый файл

        # создаём отсортированную JSON-структуру по критерию возрастания цены за килограмм
        json_data = json.dumps(sorted(self.data, key=lambda x: x[TITLES_OF_HTML[5]]), indent=4, ensure_ascii=False)

        with open(file=json_file_name, mode='w', encoding='utf-8') as json_data_file:
            json_data_file.write(json_data)  # сохраняем JSON-файл

        return 'Сканирование прайс-листов завершено.\nДанные отсортированы и сохранены в JSON-файл.'

    def search_product_price_weigth(self, headers):  # анализатор местоположения требуемых колонок данных

        for index, header in enumerate(headers):
            if not header:  # для каждого случая пустых данных в заголовке создаём уникальный ключ
                headers[index] = 'empty_header-' + str(index)

        number_product = number_price = number_weight = None

        for index, fieldname in enumerate(headers):
            if number_product is None and fieldname.lower() in KEY_WORDS_FOR_PRODUCT:
                number_product = index
            elif number_price is None and fieldname.lower() in KEY_WORDS_FOR_PRICE:
                number_price = index
            elif number_weight is None and fieldname.lower() in KEY_WORDS_FOR_WEIGHT:
                number_weight = index

        result = (number_product, number_price, number_weight)

        return result

    def export_to_html(self, fname='output.html'):  # генератор HTML-отчёта, агрегирующего все доступные прайс-листы

        with open(file=json_file_name, mode='r', encoding='utf-8') as json_data_file:
            json_data = json.load(json_data_file)

        result = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table style="white-space: nowrap; width: 100%; border-collapse: collapse">
                <tr>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[0]}</th>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[1]}</th>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[2]}</th>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[3]}</th>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[4]}</th>
                    <th style="position: sticky; top: 0; background-color: LightBlue">{TITLES_OF_HTML[5]}</th>
                </tr>
        '''
        for index, element in enumerate(json_data):
            result += '<tr>'
            result += f'<td style="border: 1px solid; text-align: center">{index + 1}</td>'

            for i in range(1, len(TITLES_OF_HTML)):
                if i == 1:
                    text_align = 'left; padding-left: 10px'
                else:
                    text_align = 'center'
                result += f'<td style="border: 1px solid; text-align: {text_align}">{element[TITLES_OF_HTML[i]]}</td>'

            result += '</tr>'

        result += '''
            </table>
        </body>
        </html>
        '''

        with open(file=fname, mode='w', encoding='utf-8') as result_file:
            result_file.write(result)

        return 'Данные экспортированы в HTML-файл.'

    def find_text(self, text):  # реализация консольного интерфейса для поисковых запросов

        with open(file=json_file_name, mode='r', encoding='utf-8') as json_data_file:
            json_data = json.load(json_data_file)

        find_positions = []  # найденные позиции в сводном прайс-листе
        self.name_length = 0

        # определение максимальной длины наименования продукции и найденных позиций
        for index, element in enumerate(json_data):
            product_name = element[TITLES_OF_HTML[1]]
            if text in product_name:
                self.name_length = max(self.name_length, len(product_name))
                find_positions.append(index)

        if not find_positions:
            return 'Совпадающие позиции не обнаружены'

        # формирование удобного к восприятию текстового ответа в консоли
        self.result = '\n'
        header = (TITLES_OF_HTML[0] + ' ' * 3 +
                  TITLES_OF_HTML[1] + ' ' * (self.name_length - len(TITLES_OF_HTML[1]) + 3) +
                  TITLES_OF_HTML[2] + ' ' * 3 +
                  TITLES_OF_HTML[3] + ' ' * 5 +
                  TITLES_OF_HTML[4] + ' ' * 5 +
                  TITLES_OF_HTML[5])
        self.result += header + '\n'
        for index, element in enumerate(json_data):
            if index in find_positions:
                line = (f'{index + 1:>4}' +
                        ' ' * 4 +
                        f'{element[TITLES_OF_HTML[1]]}' +
                        ' ' * (self.name_length - len(element[TITLES_OF_HTML[1]])) +
                        ' ' * 3 +
                        f'{element[TITLES_OF_HTML[2]]:>4}' +
                        ' ' * 6 +
                        f'{element[TITLES_OF_HTML[3]]}' +
                        ' ' * 5 +
                        f'{element[TITLES_OF_HTML[4]]}' +
                        ' ' * 5 +
                        f'{element[TITLES_OF_HTML[5]]}\n')
                self.result += line

        return self.result


pm = PriceMachine()

print(f'Запуск сканирования папки "{DIRECTORY_OF_PRICES}" и загрузка данных...')

print(pm.load_prices())

print(pm.export_to_html())

while True:

    search_text = input('Введите текст для поиска: ')

    if search_text.lower() == 'exit':
        print('Работа программы завершена.')
        break

    print(pm.find_text(search_text.lower()))
