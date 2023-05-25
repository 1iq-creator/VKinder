import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_table_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                vk_id varchar(20) NOT NULL PRIMARY KEY);"""
        )
    print("Таблица USERS создана.")


def insert_data_users(vk_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users (vk_id) 
            VALUES ('{vk_id}');"""
        )


def drop_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS users CASCADE;"""
        )
        print('Таблица USERS удалена.')


def creating_database():
    drop_users()
    create_table_users()
