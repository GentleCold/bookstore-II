import logging
import threading
from typing import Optional

import pymongo
import pymongo.errors
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from be.model.tables import Base


class Store:
    def __init__(self):
        # postgresql
        self.engine = self.get_db_conn()
        # drop out all tables befor initialize
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.database = sessionmaker(bind=self.engine)()

        # mongodb
        self.pymongo = self.get_mongo_conn()["be"]
        self.pymongo["book"].drop()
        self.pymongo["book"].create_index(["book_id"], unique=True)

    @staticmethod
    def get_db_conn():
        conn = None
        try:
            conn = create_engine("postgresql://gentle:123qwe@localhost:5432/bookstore")
        except SQLAlchemyError as e:
            print(e)
            logging.log(logging.ERROR, "Postgresql connection error")
            exit(1)
        return conn

    @staticmethod
    def get_mongo_conn():
        # 更换数据库为 mongodb
        conn = None
        try:
            conn = pymongo.MongoClient()
        except pymongo.errors.ConnectionFailure as e:
            print(e)
            logging.log(logging.ERROR, "MongDB connection error")
            exit(1)
        return conn


database_instance: Optional[Store] = None
init_completed_event = threading.Event()


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.database


def get_mongo_conn():
    global database_instance
    return database_instance.pymongo
