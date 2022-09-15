from app.context import AppContext
from datetime import datetime, timedelta
import dateutil.parser


async def get_parentId(context: AppContext, item_id):
    script = f"select parentid from item where id = '{item_id}'"
    parentId = await context.db.fetch(script)
    return parentId[0]['parentid'] if len(parentId) > 0 else None


async def get_last_update(context: AppContext, item_id):
    script = f"select max(date) from history where itemId = '{item_id}'"
    date = await context.db.fetch(script)
    return str(datetime.isoformat(date[0]['max']) + 'Z')


async def update_item(context: AppContext, item_type, item_id, url, parentId, size, date):
    parentId = 'Null' if parentId is None else "'" + str(parentId) + "'"
    size = 'Null' if size is None else size
    if item_type == 'FILE':
        script = f"update item set url = '{url}', parentId = {parentId}, size = {size} where id = '{item_id}' "
        await context.db.fetch(script)
        await create_history(context, item_id, date, 'Update file')
    if item_type == 'FOLDER':
        script = f"update item set parentId = {parentId}, size = {size} where id = '{item_id}' "
        await context.db.fetch(script)
        await create_history(context, item_id, date, 'Update folder')


async def update_folders_after_change_item(context: AppContext, folder_id, size, delta_size, date):
    script = f"update item set size = {size} where id = '{folder_id}' "
    folder_parentId = await get_parentId(context, folder_id)
    if folder_parentId is not None:
        parent_folder_size = await get_item_size(context, folder_parentId)
        await update_folders_after_change_item(context, folder_parentId,
                                               parent_folder_size + delta_size,
                                               delta_size, date)
        await create_history(context, folder_id, date, 'Update folder')

    await create_history(context, folder_id, date, 'Update folder')
    await context.db.fetch(script)


async def create_folder(context: AppContext, folder_id, parentId, date):
    parentId = 'Null' if parentId is None else "'" + str(parentId) + "'"
    script = f"insert into item (id, type, url, parentId, size) values ('{folder_id}', 'FOLDER', Null, {parentId}, 0)"
    await context.db.fetch(script)
    await create_history(context, folder_id, date, 'Create folder')


async def create_file(context: AppContext, file_id, url, parentId, size, date):
    script = f"insert into item (id, type, url, parentId, size) values ('{file_id}', 'FILE', '{url}', " \
             f"'{parentId}', {size}) "
    await context.db.fetch(script)
    await create_history(context, file_id, date, 'Create file')


async def get_item_size(context: AppContext, folder_id):
    script = f"select size from item where id = '{folder_id}'"
    size = await context.db.fetch(script)
    return int(size[0]['size'] if size[0]['size'] is not None else 0) if len(size) > 0 else 0


async def already_in_the_database(context: AppContext, item_id):
    script = f"select id from item where id = '{item_id}'"
    if len(await context.db.fetch(script)) > 0:
        return True
    else:
        return False


async def create_history(context: AppContext, item_id, date, operation):
    script = f"insert into history (itemId, operation, date) values ('{item_id}', '{operation}', '{date}')"
    await context.db.fetch(script)


async def get_foldersId(context: AppContext):
    script = f"select id from item where type = 'FOLDER'"
    folders_id = [item['id'] for item in await context.db.fetch(script)]
    return folders_id


async def get_item(context: AppContext, item_id):
    script = f"select * from item where id = '{item_id}'"
    data = await context.db.fetch(script)
    return data


async def get_item_type(context: AppContext, item_id):
    script = f"select type from item where id = '{item_id}'"
    item_type = (await context.db.fetch(script))[0]['type']
    return item_type


async def delete_from_history(context: AppContext, item_id):
    script = f"delete from history where itemId = '{item_id}'"
    await context.db.fetch(script)


async def delete_item(context: AppContext, item_id):
    await delete_from_history(context, item_id)
    script = f"delete from item where id = '{item_id}'"
    await context.db.fetch(script)


# При удалении файла из папки необходимо уменьшить вес папки
async def delete_file_in_folder(context: AppContext, item_id, delta_size, parentId, date):
    folder_size = await get_item_size(context, parentId)

    await update_folders_after_change_item(context, parentId, folder_size - delta_size, 0 - delta_size, date)
    await delete_item(context, item_id)


async def get_items_in_folder(context: AppContext, parent_Id):
    script = f"select * from item where parentId = '{parent_Id}'"
    data = await context.db.fetch(script)
    return data


async def delete_items_from_folder(context: AppContext, parent_Id):
    # Решение, на самом деле сомнительное, но нам надо удалить историю всех файлов, перед тем как их удалять
    items = await get_items_in_folder(context, parent_Id)
    for item in items:

        # Рекурсия нужна для удаления папок внутри папок
        if item['type'] == 'FOLDER':
            await delete_items_from_folder(context, item['id'])

        await delete_from_history(context, item['id'])

    script = f"delete from item where parentId = '{parent_Id}'"
    await context.db.fetch(script)


async def move_item(context: AppContext, item_id, item_new_parent_Id, url, date):
    # Данные Item в бд
    item_in_database = await get_item(context, item_id)

    item_size = await get_item_size(context, item_id)

    # Если item перемещают
    if item_in_database[0]['parentid'] != item_new_parent_Id:

        # Изменяем вес старой родительской папки
        parent_folder_size = await get_item_size(context, item_in_database[0]['parentid'])
        await update_folders_after_change_item(context, item_in_database[0]['parentid'],
                                               parent_folder_size - item_size, 0 - item_size, date)

        # Если её перемещают в другую папку
        if item_new_parent_Id is not None:

            new_parent_folder_size = await get_item_size(context, item_new_parent_Id)

            # Изменить вес родительской папки
            await update_folders_after_change_item(context, item_new_parent_Id,
                                                   new_parent_folder_size + item_size,
                                                   item_size, date)

            # Изменить сам item
            print('size 174 строка', item_size)
            await update_item(context, item_in_database[0]['type'], item_id, url, item_new_parent_Id, item_size,
                              date)

            # Если её перемещают в корневую директорию
        else:
            print('size 180 строка', item_size)
            await update_item(context, item_in_database[0]['type'], item_id, url, None, item_size,
                              date)


async def import_items(context: AppContext, data):
    date = data['updateDate']
    folders = []
    files = []

    # Разделяем файлы и папки
    for item in data['items']:
        if item['type'] == 'FOLDER':
            folders.append(item)
        elif item['type'] == 'FILE':
            files.append(item)

    # родителем элемента может быть только папка
    # проверка на то, есть ли такой parentId, не указывающий на папку
    parentId_set = set(file['parentId'] for file in files)
    foldersId_set = set(folder['id'] for folder in folders)
    for file_parentId in parentId_set:
        if file_parentId not in foldersId_set and file_parentId not in await get_foldersId(
                context) and file_parentId is not None:
            return False

    for folder in folders:

        # Если родитель родителя та папка, которую импортируют. (проверка на цикл)
        if await get_parentId(context, folder['parentId']) == folder['id']:
            return False

        if await already_in_the_database(context, folder['id']):
            await move_item(context, folder['id'], folder['parentId'], None, date)
            continue

        await create_folder(context, folder['id'], folder['parentId'], date)

    for file in files:
        file_id = file['id']
        url = file['url']
        parentId = file['parentId']
        size = file['size']

        # Проверка на то есть ли уже такой файл
        if await already_in_the_database(context, file_id):
            await move_item(context, file['id'], file['parentId'], file['url'], date)
            continue
        # Обновить вес папки при добавлении файла
        if parentId is not None:
            old_file_size = await get_item_size(context, file_id)
            delta_size = size - old_file_size

            if delta_size != 0:
                folder_size = await get_item_size(context, parentId)
                await update_folders_after_change_item(context, parentId, folder_size + delta_size, delta_size,
                                                       date)

        await create_file(context, file_id, url, parentId, size, date)

    return True


async def delete_element(context: AppContext, data, date):
    item = (await get_item(context, data))[0]

    if item['type'] == 'FILE':
        await delete_file_in_folder(context, item['id'], item['size'], item['parentid'], date)

    if item['type'] == 'FOLDER':

        # Если в папке что-то есть, удаляем содержимое
        if len(await get_items_in_folder(context, item['id'])) > 0:
            await delete_items_from_folder(context, item['id'])
            await delete_item(context, item['id'])
        # Если папка пустая, просто удаляем папку
        else:
            await delete_item(context, item['id'])

        if item['parentid'] is not None:
            if item['size'] != 0:
                folder_size = await get_item_size(context, item['parentid'])
                await update_folders_after_change_item(context, item['parentid'], folder_size - item['size'],
                                                       -item['size'],
                                                       date)
    return True


async def get_nodes(context: AppContext, data):
    item = (await get_item(context, data))[0]

    if item['type'] == 'FILE':
        return {
            'id': item['id'],
            'type': item['type'],
            'url': item['url'],
            'parentId': item['parentid'],
            'date': await get_last_update(context, item['id']),
            'size': item['size'],
            'children': None
        }

    if item['type'] == 'FOLDER':
        final_dict = await create_nodes_dict(context, item)
        return final_dict


async def create_nodes_dict(context: AppContext, item):
    if item['type'] == 'FILE':
        return {
            'id': item['id'],
            'type': item['type'],
            'url': item['url'],
            'parentId': item['parentid'],
            'date': await get_last_update(context, item['id']),
            'size': item['size'],
            'children': None
        }

    if item['type'] == 'FOLDER':
        if len(await get_items_in_folder(context, item['id'])) > 0:
            intermediate_dict = {
                'id': item['id'],
                'type': item['type'],
                'url': item['url'],
                'parentId': item['parentid'],
                'date': await get_last_update(context, item['id']),
                'size': item['size'],
                'children': []
            }
            items = await get_items_in_folder(context, item['id'])

            for item in items:
                intermediate_dict['children'].append(await create_nodes_dict(context, item))

            return intermediate_dict
        else:
            return {
                'id': item['id'],
                'type': item['type'],
                'url': item['url'],
                'parentId': item['parentid'],
                'date': await get_last_update(context, item['id']),
                'size': item['size'],
                'children': []
            }


async def get_items_updated_in_last_day(context: AppContext, date):
    end_date = dateutil.parser.parse(date)
    start_date = end_date - timedelta(days=1)

    items = await get_files_updated_in_snippet(context, start_date, end_date)

    updated_files = []
    for item in items:
        data = (await get_item(context, item['itemid']))[0]
        if data['type'] == 'FILE':
            updated_files.append({
                "id": data['id'],
                "url": data['url'],
                "date": str(datetime.isoformat(item['date']) + 'Z'),
                "parentId": data['parentid'],
                "size": data['size'],
                "type": data['type']
            })
    return updated_files


async def get_files_updated_in_snippet(context: AppContext, start_date, end_date):
    script = f"select distinct itemId, date from history where date >= '{start_date}' and date <= '{end_date}'"
    return await context.db.fetch(script)


async def get_item_history(context: AppContext, item_id, date_start, date_end):
    history = await get_item_history_in_interval(context, item_id, date_start, date_end)
    answer = []
    for item in history:
        answer.append({
            "date": str(datetime.isoformat(item['date']) + 'Z'),
            "operation": item['operation']
        })
    return answer


async def get_item_history_in_interval(context: AppContext, item_id, date_start, date_end):
    script = f"select * from history where date >= '{date_start}' and date < '{date_end}' and itemId = '{item_id}'"
    return await context.db.fetch(script)
