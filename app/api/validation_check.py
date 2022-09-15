from datetime import datetime


def datetime_valid(date):
    try:
        datetime.fromisoformat(date.replace('Z', '+00:00'))

    except ValueError:
        return False
    return True


def check_json(data):
    # дата обрабатывается согласно ISO 8601
    if not datetime_valid(data['updateDate']):
        return False

    folders = []
    files = []
    items_id = []
    # Разделяем файлы и папки
    for item in data['items']:

        # поле id не может быть равно null
        if item['id'] is None:
            return False

        # размер поля url при импорте файла всегда должен быть меньше либо равным 255
        if item['type'] == 'FILE' and len(item['url']) > 255:
            return False

        # поле size для файлов всегда должно быть больше 0
        if item['type'] == 'FILE' and item['size'] <= 0:
            return False

        items_id.append(item['id'])

        # Папка не может быть своим родителем
        if item['type'] == "FOLDER" and item['parentId'] == item['id']:
            return False

        # TODO: Убрать?
        if item['type'] == 'FOLDER':
            folders.append(item)
        elif item['type'] == 'FILE':
            files.append(item)

    # в одном запросе не может быть двух элементов с одинаковым id
    if len(set(items_id)) < len(data['items']):
        return False

    return True


def check_item_id(item_id):
    # поле id не может быть равно null
    if item_id is None or item_id == 'None':
        return False

    return not_sql_injection(item_id)


def not_sql_injection(field):
    # проверка на кавычки, которые могут быть использованы для sql иньекции
    if (str(field).find("'") or str(field).find('"')) != -1:
        return False
    return True
