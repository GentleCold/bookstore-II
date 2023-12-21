from be.model import store
from be.model.tables import StoreBookTable, StoreTable, UserTable


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()()
        self.mongo = store.get_mongo_conn()

    def user_id_exist(self, user_id):
        result = self.conn.query(UserTable).filter_by(user_id=user_id).first()
        if result is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        result = (
            self.conn.query(StoreBookTable)
            .filter_by(store_id=store_id, book_id=book_id)
            .first()
        )
        if result is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        result = self.conn.query(StoreTable).filter_by(store_id=store_id).first()
        if result is None:
            return False
        else:
            return True
