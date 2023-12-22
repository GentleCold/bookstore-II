import uuid

import pytest
from flask.app import json

from fe import conf
from fe.access.new_buyer import register_new_buyer
from fe.access.search import Search
from fe.test.gen_book_data import GenBook


class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_search_user_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, _ = self.gen_book.gen(False, False)
        assert ok
        self.search = Search(conf.URL, self.buyer.token)

        # generate Store_Num_Total stores
        for i in range(conf.Store_Num_Total):
            seller_id = ("test_search_seller_id_{}" + str(i)).format(str(uuid.uuid1()))
            store_id = ("test_search_store_id_{}" + str(i)).format(str(uuid.uuid1()))
            GenBook(seller_id, store_id).gen(False, False)

        yield

    def test_search_store_with_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        fields = ["tags", "book_intro", "content"]
        code, _ = self.search.search(key, self.store_id, fields)
        print(json.dumps(_))
        assert code == 200

    def test_search_store_without_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        code, _ = self.search.search(key, self.store_id, None)
        assert code == 200

    def test_search_global_with_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        fields = ["tags", "author", "book_intro"]
        code, _ = self.search.search(key, None, fields)
        assert code == 200

    def test_search_global_without_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        code, _ = self.search.search(key, None, None)
        assert code == 200

    def test_non_exist_store_id(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        code, _ = self.search.search(key, self.store_id + "x", None)
        assert code != 200

    def test_non_result(self):
        key = "book_info[0].title"
        fields = ["title", "book_intro"]
        code, _ = self.search.search(key, None, fields)
        assert code != 200

    def test_non_result_in_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].tags[0]
        fields = ["author"]
        code, _ = self.search.search(key, None, fields)
        assert code != 200

    def test_non_exist_fields(self):
        book_info = self.gen_book.buy_book_info_list[0]
        key = book_info[0].title
        fields = ["table"]
        code, _ = self.search.search(key, None, fields)
        assert code != 200
