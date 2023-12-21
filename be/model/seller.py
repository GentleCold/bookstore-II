from typing import Tuple

from pymongo.errors import OperationFailure
from sqlalchemy.exc import SQLAlchemyError

from be.model import db_conn, error
from be.model.tables import OrderTable, StoreBookTable, StoreTable


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_info,
        stock_level: int,
    ):
        book_id = book_info.get("id")
        price = book_info.get("price")
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            store = StoreBookTable(
                store_id=store_id, book_id=book_id, price=price, stock_level=stock_level
            )
            self.conn.add(store)
            self.conn.commit()

            self.mongo["book"].insert_one(book_info)
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except OperationFailure as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.query(StoreBookTable).filter_by(
                store_id=store_id, book_id=book_id
            ).update({"stock_level": StoreBookTable.stock_level + add_stock_level})

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> Tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            store = StoreTable(store_id=store_id, user_id=user_id)
            self.conn.add(store)
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship(self, order_id: str, store_id: str, user_id: str) -> Tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            order = (
                self.conn.query(OrderTable.store_id, OrderTable.state)
                .filter_by(order_id=order_id)
                .first()
            )

            # 不存在订单
            if order is None:
                return error.error_invalid_order_id(order_id)

            state = order[1]

            # 不匹配商店
            if store_id != order[0]:
                return error.error_not_corresponding_store(store_id, order_id)

            store = (
                self.conn.query(StoreTable.user_id).filter_by(store_id=store_id).first()
            )

            # 不匹配卖家
            if user_id != store[0]:
                return error.error_not_corresponding_seller(user_id, order_id)

            # 非期待订单状态
            if state != 1:
                return error.error_unexpected_order_status(order_id, "paid")

            # 发货，更新状态
            self.conn.query(OrderTable).filter_by(order_id=order_id).update(
                {"state": 2}
            )
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)
        return 200, "ok"
