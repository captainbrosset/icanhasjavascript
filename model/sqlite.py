import sqlite3
import os
import model
import platform


if platform.system() == "Windows":
    DB_STORAGE_ROOT = "C:\\Temp\\"
else:
    DB_STORAGE_ROOT = "/tmp/"
DB_PATH = DB_STORAGE_ROOT + "icanhasjavascript"
DB_NAME = "db"


class Storage(object):

    def __init__(self):
        self.init()

    def init(self):
        self.create_db_dir()
        self.connection = sqlite3.connect(self.get_full_db_name())
        self.create_entity_table()

    def get_full_db_name(self):
        return os.sep.join([DB_PATH, DB_NAME])

    def create_db_dir(self):
        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

    def open_execute_and_close(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def create_entity_table(self):
        self.open_execute_and_close("create table if not exists entities (name text, file text, type text, arguments text)")

    def get_files_model(self, files):
        entities = []
        cursor = self.connection.cursor()
        for file in files:
            results = cursor.execute("select * from entities where file = '" + file + "'")
            for result in results.fetchall():
                if result[2] == "variable":
                    entities.append(model.Variable(file, result[0]))
                elif result[2] == "function":
                    entities.append(model.Function(file, result[0], result[3]))
        cursor.close()
        return entities

    def update_file_model(self, file, entities):
        cursor = self.connection.cursor()
        cursor.execute("delete from entities where file='" + file + "'")
        for entity in entities:
            type = "variable"
            arguments = ""
            if hasattr(entity, "arguments"):
                arguments = ",".join(entity.arguments)
                type = "function"
            cursor.execute("insert into entities values('" + entity.name + "', '" + file + "', '" + type + "', '" + str(arguments) + "')")
        self.connection.commit()
        cursor.close()

    def flush_model(self):
        self.open_execute_and_close("drop table entities")
        self.init()


if __name__ == "__main__":
    storage = Storage()
    #storage.open_execute_and_close("insert into entities values('test', 'script.js', 'testdir2', '1,2,3')")
    #storage.open_execute_and_close("insert into entities values('test33', 'script2.js', 'testdir2', '')")
    #storage.flush_model()
    cursor = storage.connection.cursor()
    results = cursor.execute("select * from entities")
    results = results.fetchall()
    for r in results:
        print r
    storage.connection.commit()
    cursor.close()
