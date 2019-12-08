import sqlite3
import mysql.connector as mysql


class StorageSqlite:
    def __init__(self, db_name, schema=None):
        try:
            self.connection = sqlite3.connect(db_name)
        except sqlite3.Error as e:
            print('Error while connecting to sqlite', e)
        if schema:
            self.connection.execute(schema)

    def write(self, query, data):
        try:
            with self.connection:
                self.connection.execute(query, data)
        except sqlite3.IntegrityError as e:
            print('Error occured: ', e)
            return False
        else:
            return True

    def close(self):
        self.connection.close()


class StorageMysql:
    def __init__(self, host, user, password, db_name):
        try:
            self.connection = mysql.connect(host, user, password, db_name)
            self.cursor = self.connection.cursor()
        except mysql.Error as e:
            print('Error while connecting to MySQL', e)

    def write(self, query, data):
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
        except mysql.Error as e:
            print('Error occured', e)
            self.connection.rollback()
            return False
        else:
            return True

    def close(self):
        self.cursor.close()
        self.connection.close()
