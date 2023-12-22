import json
from typing import Optional, Tuple

import pymongo.errors
from sqlalchemy.exc import SQLAlchemyError

from be.model import db_conn, error
from be.model.tables import StoreBookTable


def _check_fields(fields):
    allowed_fields = [
        "id",
        "tags",
        "title",
        "author",
        "publisher",
        "original_title",
        "translator",
        "pub_year",
        "author_intro",
        "book_intro",
        "content",
    ]
    for field in fields:
        if field not in allowed_fields:
            return False
    return True


class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search(
        self, key: str, store_id: Optional[str], fields: Optional[list]
    ) -> Tuple[int, str, list]:
        results = []
        try:
            books = None
            key = json.dumps(key)
            if store_id is None:  # global search
                books = self.mongo["book"].find({"$text": {"$search": key}})
            else:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id) + ([],)
                books = self.mongo["book"].find(
                    {"store_id": store_id, "$text": {"$search": key}}
                )
            key = json.loads(key)

            for book in books:
                correspond = False
                if fields is not None and not _check_fields(fields):
                    return error.error_invalid_fields() + ([],)

                book_id = book["book_id"]
                store_id = book["store_id"]

                if fields is not None:
                    book_info = json.loads(book["book_info"])
                    for field in fields:
                        if key in book_info[field]:
                            correspond = True
                            break

                if correspond or fields is None:
                    stock_level = (
                        self.conn.query(StoreBookTable.stock_level)
                        .filter_by(store_id=store_id, book_id=book_id)
                        .first()[0]
                    )
                    results.append(
                        {
                            "store_id": store_id,
                            "book_id": book_id,
                            "book_info": book["book_info"],
                            "pictures": book["pictures"],
                            "stock_level": stock_level,
                        }
                    )

            if not results:
                return error.error_non_exist_search_result() + ([],)
        except pymongo.errors.OperationFailure as e:
            return 528, "{}".format(str(e)), []
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            # print(e)
            return 530, "{}".format(str(e)), []

        return 200, "ok", results
