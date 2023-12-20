import logging
import uuid
from typing import List, Tuple

from sqlalchemy.exc import SQLAlchemyError

from be.model import db_conn, error
from be.model.tables import (
    OrderDetailTable,
    OrderTable,
    StoreBookTable,
    StoreTable,
    UserTable,
)


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: List[Tuple[str, int]]
    ) -> Tuple[int, str, str]:
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = (
                    self.conn.query(
                        StoreBookTable.price,
                        StoreBookTable.stock_level,
                    )
                    .filter_by(store_id=store_id, book_id=book_id)
                    .first()
                )
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                price = result[0]
                stock_level = result[1]

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result = self.conn.query(StoreBookTable).filter(
                    StoreBookTable.store_id == store_id,
                    StoreBookTable.book_id == book_id,
                    StoreBookTable.stock_level >= count,
                )
                if result is None:
                    return error.error_stock_level_low(book_id) + (order_id,)
                result.update({"stock_level": StoreBookTable.stock_level - count})

                order_detail = OrderDetailTable(
                    order_id=uid,
                    book_id=book_id,
                    count=count,
                    price=price,
                )
                self.conn.add(order_detail)

            order = OrderTable(order_id=uid, user_id=user_id, store_id=store_id)
            self.conn.add(order)
            self.conn.commit()
            order_id = uid
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> Tuple[int, str]:
        conn = self.conn
        try:
            order = (
                conn.query(OrderTable.order_id, OrderTable.user_id, OrderTable.store_id)
                .filter_by(order_id=order_id)
                .first()
            )
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_id = order[0]
            buyer_id = order[1]
            store_id = order[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # find buyer
            buyer = (
                conn.query(UserTable.balance, UserTable.password)
                .filter_by(user_id=buyer_id)
                .first()
            )
            if buyer is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = buyer[0]
            if password != buyer[1]:
                return error.error_authorization_fail()

            # find seller
            seller = conn.query(StoreTable.user_id).filter_by(store_id=store_id).first()
            if seller is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = seller[0]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # calculate total price
            infos = (
                conn.query(
                    OrderDetailTable.count,
                    OrderDetailTable.price,
                )
                .filter_by(order_id=order_id)
                .all()
            )
            total_price = 0
            for info in infos:
                count = info[0]
                price = info[1]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # update buyer balance
            buyer_update = conn.query(UserTable).filter(
                UserTable.user_id == buyer_id, UserTable.balance >= total_price
            )
            if buyer_update is None:
                return error.error_not_sufficient_funds(order_id)
            buyer_update.update({"balance": UserTable.balance - total_price})

            # update seller balance
            seller_update = conn.query(UserTable).filter_by(user_id=seller_id)

            if seller_update == 0:
                return error.error_non_exist_user_id(seller_id)
            seller_update.update({"balance": UserTable.balance + total_price})

            # delete order
            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            #
            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> Tuple[int, str]:
        try:
            # find user
            user = (
                self.conn.query(UserTable.password).filter_by(user_id=user_id).first()
            )
            if user is None:
                return error.error_authorization_fail()

            if user[0] != password:
                return error.error_authorization_fail()

            # update balance
            self.conn.query(UserTable).filter_by(user_id=user_id).update(
                {"balance": UserTable.balance + add_value}
            )

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
