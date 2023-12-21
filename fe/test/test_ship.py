import uuid
from typing import List

import pytest

from fe.access.book import Book
from fe.access.buyer import Buyer
from fe.access.new_buyer import register_new_buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook


class TestShip:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: List[Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_ship_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_ship_store_id_{}".format(str(uuid.uuid1()))
        self.store_id_2 = "test_ship_store_id_2{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_ship_buyer_id_{}".format(str(uuid.uuid1()))
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

        # 买家充值后支付
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200

        yield

    def test_ok(self):
        # 卖家发货
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 200

    def test_not_valid_order(self):
        code = self.seller.ship(self.order_id + "_x", self.store_id)
        assert code == 518

    def test_repeat_ship(self):
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 200

        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 523

    def test_non_exist_user_id(self):
        self.seller.seller_id = self.seller.seller_id + "_x"
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 511

    def test_non_exist_store_id(self):
        code = self.seller.ship(self.order_id, self.store_id + "_x")
        assert code == 513

    def test_not_corresponding_user_id(self):
        self.seller.seller_id = self.buyer_id
        code = self.seller.ship(self.order_id, self.store_id)
        assert code == 520

    def test_not_corresponding_store_id(self):
        code = self.seller.create_store(self.store_id_2)
        assert code == 200
        code = self.seller.ship(self.order_id, self.store_id_2)
        assert code == 522
