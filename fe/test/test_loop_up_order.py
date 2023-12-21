import uuid
from typing import List

import pytest

from fe.access.book import Book
from fe.access.buyer import Buyer
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook


class TestLookUpOrder:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: List[Book]
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_look_up_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_look_up_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_look_up_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        # 10 orders
        for i in range(10):
            gen_book = GenBook(self.seller_id + str(i), self.store_id + str(i))
            ok, buy_book_id_list = gen_book.gen(
                non_exist_book_id=False, low_stock_level=False, max_book_count=5
            )
            self.buy_book_info_list = gen_book.buy_book_info_list
            assert ok
            code, self.order_id = b.new_order(self.store_id + str(i), buy_book_id_list)
            assert code == 200

        yield

    def test_ok(self):
        code, _ = self.buyer.look_up_order()
        assert code == 200
        assert len(_) == 10

    def test_non_exist_user_id(self):
        self.buyer.user_id += "_x"
        code, _ = self.buyer.look_up_order()
        assert code == 511
