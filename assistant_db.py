import pymysql

class AssistantDB():
    def __init__(self, host, user, password, db):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)

    def add_transcript(self, trascript_data):
        with self.conn.cursor() as cursor:
            sql = "insert into transcript(body, info) values(%s, %s)"
            cursor.execute(sql, trascript_data)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
