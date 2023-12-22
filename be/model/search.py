from typing import Optional, Tuple

import pymongo.errors
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_searchable import search

from be.model import db_conn, error
from be.model.tables import BookTable, StoreBookTable, allowed_fields


def _check_fields(fields):
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
            query = search(select(BookTable), key)

            if store_id:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id) + ([],)
                query = query.filter(BookTable.store_id == store_id)

            books = self.conn.scalars(query).all()

            for book in books:
                book_table_dict = {
                    column.name: getattr(book, column.name)
                    for column in book.__table__.columns
                    if column.name != "search_vector"
                }

                # check fields
                if fields:
                    if not _check_fields(fields):
                        return error.error_invalid_fields() + ([],)
                    correspond = False
                    for field in fields:
                        if key in book_table_dict[field]:
                            correspond = True
                            break
                    if not correspond:
                        continue

                blob = self.mongo["book"].find_one(
                    {"store_id": book.store_id, "book_id": book.id}
                )

                info = (
                    self.conn.query(StoreBookTable.price, StoreBookTable.stock_level)
                    .filter_by(store_id=book.store_id, book_id=book.id)
                    .first()
                )

                book_table_dict["pictures"] = blob["pictures"]
                book_table_dict["content"] = blob["content"]
                book_table_dict["price"] = info[0]
                book_table_dict["stock_level"] = info[1]
                results.append(book_table_dict)

            if not results:
                return error.error_non_exist_search_result() + ([],)
        except pymongo.errors.OperationFailure as e:
            return 528, "{}".format(str(e)), []
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e)), []

        return 200, "ok", results
