import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_table_viewed():
    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS viewed (
                    profile_id INT,
                    worksheet_id INT
                )'''
        )
    print("Таблица viewed создана.")


def add_users(vk_id, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO viewed (profile_id, worksheet_id) 
            VALUES ('{vk_id}', '{user_id}');"""
        )


def check_users(vk_id, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM viewed WHERE profile_id = {vk_id} AND worksheet_id = {user_id}"""
        )
        result = cursor.fetchone()
    return True if result else False


def drop_viewed():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS viewed CASCADE;"""
        )
        print('Таблица viewed удалена.')


def creating_database():
    drop_viewed()
    create_table_viewed()