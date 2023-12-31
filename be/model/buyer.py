import logging
import uuid
from time import time
from typing import List, Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from be.model import db_conn, error
from be.model.tables import (OrderDetailTable, OrderTable, StoreBookTable,
                             StoreTable, UserTable)


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
                        StoreBookTable,
                    )
                    .filter_by(store_id=store_id, book_id=book_id)
                    .first()
                )
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                result.stock_level -= count

                order_detail = OrderDetailTable(
                    order_id=uid,
                    book_id=book_id,
                    count=count,
                    price=result.price,
                )
                self.conn.add(order_detail)

            now = time()
            order = OrderTable(
                order_id=uid, user_id=user_id, store_id=store_id, state=0, time=now
            )
            self.conn.add(order)
            self.conn.commit()
            order_id = uid
        except SQLAlchemyError as e:
            print(e)
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
                conn.query(OrderTable)
                .filter_by(order_id=order_id)
                .options(joinedload(OrderTable.user))
                .first()
            )
            if order is None:
                return error.error_invalid_order_id(order_id)

            if order.user_id != user_id:
                return error.error_authorization_fail()

            # find buyer
            # NOTE: 添加外键约束后不用额外判断
            # buyer = (
            #     conn.query(UserTable.balance, UserTable.password)
            #     .filter_by(user_id=buyer_id)
            #     .first()
            # )
            # if buyer is None:
            #     return error.error_non_exist_user_id(buyer_id)

            if password != order.user.password:
                return error.error_authorization_fail()

            # 非期待订单状态
            if order.state != 0:
                return error.error_unexpected_order_status(order_id, "unpaid")
            else:
                # 设置超时则取消订单
                if time() - order.time > 1:  # 为方便测试，设置1秒超时
                    # 返还商家商品
                    self._return_to_store(order_id)
                    # 更新订单状态
                    order.state = 4
                    self.conn.commit()
                    return error.error_order_timeout(order_id)

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

            if order.user.balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # update buyer balance, exclude seller, unless buyer pick the books
            order.user.balance -= total_price

            # update state of order
            order.state = 1
            conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> Tuple[int, str]:
        try:
            # find user
            user = self.conn.query(UserTable).filter_by(user_id=user_id).first()
            if user is None:
                return error.error_authorization_fail()

            if user.password != password:
                return error.error_authorization_fail()

            # update balance
            user.balance += add_value

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def pick(self, user_id: str, order_id: str) -> Tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            order = (
                self.conn.query(OrderTable)
                .filter_by(order_id=order_id)
                .options(joinedload(OrderTable.store).joinedload(StoreTable.user))
                .first()
            )

            # 不存在订单
            if order is None:
                return error.error_invalid_order_id(order_id)

            # 不匹配买家
            if user_id != order.user_id:
                return error.error_not_corresponding_buyer(user_id, order_id)

            # 预期订单为发货状态
            if order.state != 2:
                return error.error_unexpected_order_status(order_id, "ship")

            # 收货，更新状态
            order.state = 3

            # 获得订单详细信息
            # calculate total price
            infos = (
                self.conn.query(
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

            # update seller balance
            order.store.user.balance += total_price

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def look_up_order(self, user_id: str) -> Tuple[int, str, list]:
        orders = []
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ([],)

            results = (
                self.conn.query(
                    OrderTable.order_id,
                    OrderTable.store_id,
                    OrderTable.state,
                    OrderTable.time,
                )
                .filter_by(user_id=user_id)
                .all()
            )

            for order in results:
                order_id = order[0]
                store_id = order[1]
                state = order[2]
                order_time = order[3]
                books = []

                details = (
                    self.conn.query(
                        OrderDetailTable.book_id,
                        OrderDetailTable.count,
                        OrderDetailTable.price,
                    )
                    .filter_by(order_id=order_id)
                    .all()
                )
                for detail in details:
                    book_id = detail[0]
                    count = detail[1]
                    price = detail[2]
                    books.append({"book_id": book_id, "count": count, "price": price})

                orders.append(
                    {
                        "order_id": order_id,
                        "store_id": store_id,
                        "state": state,
                        "time": order_time,
                        "books": books,
                    }
                )
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []

        return 200, "ok", orders

    def cancel_order(self, user_id: str, order_id: str) -> Tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            order = (
                self.conn.query(OrderTable)
                .filter_by(order_id=order_id)
                .options(joinedload(OrderTable.user))  # 加载关联的 UserTable 对象
                .first()
            )

            # 不存在订单
            if order is None:
                return error.error_invalid_order_id(order_id)

            state = order.state

            # 不匹配买家
            if user_id != order.user.user_id:
                return error.error_not_corresponding_buyer(user_id, order_id)

            # 如果订单没有处于取消状态或者已收货状态，那就可以取消
            if state != 4 and state != 3:
                # 将商品返还给卖家
                self._return_to_store(order_id)
                # 如果买家已经付款，返还付款
                if state != 0:
                    # 获得订单详细信息
                    results = (
                        self.conn.query(OrderDetailTable.count, OrderDetailTable.price)
                        .filter_by(order_id=order_id)
                        .all()
                    )
                    total_price = 0
                    for row in results:
                        count = row[0]
                        price = row[1]
                        total_price = total_price + price * count

                    order.user.balance += total_price

                # 更新状态
                order.state = 4
                self.conn.commit()
            else:
                return error.error_unexpected_order_status(order_id, "not paid or pick")

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def _return_to_store(self, order_id: str):
        """
        将商品返还给商店
        """
        details = (
            self.conn.query(OrderDetailTable.book_id, OrderDetailTable.count)
            .filter_by(order_id=order_id)
            .all()
        )

        store_id = (
            self.conn.query(OrderTable.store_id).filter_by(order_id=order_id).first()[0]
        )

        for detail in details:
            book_id = detail[0]
            count = detail[1]

            self.conn.query(StoreBookTable).filter_by(
                store_id=store_id, book_id=book_id
            ).update({"stock_level": StoreBookTable.stock_level + count})
