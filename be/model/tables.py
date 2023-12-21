from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

# from sqlalchemy.orm import relationship

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "user_table"

    user_id = Column(String, primary_key=True)
    password = Column(String)
    balance = Column(Integer)
    token = Column(String, nullable=True)
    terminal = Column(String, nullable=True)


class StoreTable(Base):
    __tablename__ = "store_table"

    store_id = Column(String, primary_key=True)
    user_id = Column(String)


class OrderTable(Base):
    __tablename__ = "order_table"

    order_id = Column(String, primary_key=True)
    user_id = Column(String)
    store_id = Column(String)
    state = Column(Integer)
    time = Column(Float)


class StoreBookTable(Base):
    __tablename__ = "store_book_table"

    store_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    price = Column(Integer)
    stock_level = Column(Integer)


class OrderDetailTable(Base):
    __tablename__ = "order_detail_table"

    order_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    count = Column(Integer)
    price = Column(Integer)
