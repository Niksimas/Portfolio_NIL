import sqlite3

from core.statistics.basic import set_statistic
from core.settings import settings, home


def save_new_user(user_id: int, link: str) -> None:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        data = [user_id, link]
        cursor = connect.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM all_user where user_id = $1)', [user_id])
        if bool(cursor.fetchall()[0][0]):
            return
        set_statistic("new_user")
        cursor.execute('INSERT INTO main.all_user (user_id, link) VALUES(?, ?);', data)


def get_all_id_user() -> list[int]:
    """:return: список id всех пользователей"""
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM main.all_user')
        list_id = cursor.fetchall()
        result = [i[0] for i in list_id]
    return result


def get_all_id_admin() -> list[int]:
    """:return: список id администраторов"""
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id FROM main.all_user WHERE admin=true')
        list_id = cursor.fetchall()
        result = [i[0] for i in list_id]
        result.append(settings.bots.admin_id)
    return result


def get_all_data_admin() -> dict:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id, name FROM main.all_user WHERE admin=true')
        list_id = cursor.fetchall()
        result = {i[0]: i[1] for i in list_id}
    return result


def save_new_admin(user_id: int, link: str, name:str) -> None:
    save_new_user(user_id, link)
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('UPDATE main.all_user SET admin=true, name=$1 WHERE user_id=$2', [name, user_id])


def get_project_data(project_id: int, type_proj: str) -> dict:
    try:
        with sqlite3.connect(f"{home}/database/main_data.db") as connect:
            cursor = connect.cursor()
            cursor.execute(f'SELECT * FROM main.{type_proj} WHERE id=$1', [project_id])
            data = cursor.fetchall()[0]
            result = {"id": data[0], "name_photo": data[1], "name_project": data[2], "description": data[3]}
            return result
    except IndexError:
        return {}


def get_review_data(project_id: int) -> dict:
    try:
        with sqlite3.connect(f"{home}/database/main_data.db") as connect:
            cursor = connect.cursor()
            cursor.execute(f'SELECT * FROM main.review WHERE id=$1', [project_id])
            data = cursor.fetchall()[0]
            result = {"id": data[0], "name_project": data[1], "text": data[2], "name": data[3]}
            return result
    except IndexError:
        return {}


def get_mess(type_mess: str) -> str:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT text FROM main.message WHERE type_message=$1', [type_mess])
        return cursor.fetchall()[0][0]


def get_user(user_id: int) -> str:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT name FROM main.all_user WHERE user_id=$1', [user_id])
        return cursor.fetchall()[0][0]


def set_mess(type_mess: str, text: str, photo_name: str = None) -> None:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('UPDATE main.message SET text=$1, name_photo=$2 WHERE type_message=$3',
                       [text, photo_name, type_mess])


def get_project_all_id(type_proj: str) -> list:
    try:
        with sqlite3.connect(f"{home}/database/main_data.db") as connect:
            cursor = connect.cursor()
            cursor.execute(f'SELECT id FROM main.{type_proj}')
            data = cursor.fetchall()
            result = [i[0] for i in data]
            return result
    except IndexError:
        return []


def get_reviews_all_id() -> list:
    try:
        with sqlite3.connect(f"{home}/database/main_data.db") as connect:
            cursor = connect.cursor()
            cursor.execute(f'SELECT id FROM main.review WHERE verification=true')
            data = cursor.fetchall()
            result = [i[0] for i in data]
            return result
    except IndexError:
        return []


def save_new_review(data: dict) -> int:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('INSERT INTO main.review (name_project, text, name) VALUES(?, ?, ?) RETURNING id;',
                       [data["name_project"], data["text"], data["name"]])
        data = cursor.fetchall()
        return data[0][0]


def verification_review(review_id: int) -> None:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('UPDATE main.review SET verification=true '
                       'WHERE id=$1', [review_id])


def deleted_review(review_id: int):
    with sqlite3.connect(f"{home}/BD/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'DELETE FROM main.review WHERE id=$1',
                       [review_id])


def deleted_admin(user_id: int):
    with sqlite3.connect(f"{home}/BD/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.all_user SET admin=false WHERE user_id=$1',
                       [user_id])
