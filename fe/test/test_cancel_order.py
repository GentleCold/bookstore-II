import time

import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid


class TestCancelOrder:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        # 构造一批图书，生成图书时已经将书本加入商店
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok

        self.seller = gen_book.seller

        # 注册买家
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b

        # 下单
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        # 计算总价格
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        # 买家充值
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        yield

    def test_ok(self):
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

    def test_ok_after_pay(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

    def test_ok_after_ship(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

    def test_cancel_after_pick(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 200
        code = self.buyer.pick(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id)
        assert code == 523

    def test_cancel_order_if_timeout(self):
        time.sleep(1)
        code = self.buyer.payment(self.order_id)
        assert code == 524
        code = self.buyer.cancel_order(self.order_id)
        assert code == 523

    def test_not_valid_order(self):
        code = self.buyer.cancel_order(self.order_id + '_x')
        assert code == 518

    def test_repeat_cancel(self):
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

        code = self.buyer.cancel_order(self.order_id)
        assert code == 523

    def test_non_exist_user_id(self):
        self.buyer.user_id = self.buyer.user_id + '_x'
        code = self.buyer.cancel_order(self.order_id)
        assert code == 511

    def test_not_corresponding_user_id(self):
        self.buyer.user_id = self.seller_id
        code = self.buyer.cancel_order(self.order_id)
        assert code == 521
