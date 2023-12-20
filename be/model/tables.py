from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.orm import relationship

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "user"

    user_id = Column(String, primary_key=True)
    password = Column(String)
    balance = Column(Integer)
    token = Column(String, nullable=True)
    terminal = Column(String, nullable=True)


class StoreTable(Base):
    __tablename__ = "store"

    store_id = Column(String, primary_key=True)
    user_id = Column(String)


class OrderTable(Base):
    __tablename__ = "order"

    order_id = Column(String, primary_key=True)
    user_id = Column(String)
    store_id = Column(String)
    state = Column(Integer)
    time = Column(Float)


class StoreBookTable(Base):
    __tablename__ = "store_book"

    store_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    price = Column(Integer)
    stock_level = Column(Integer)


class OrderDetailTable(Base):
    __tablename__ = "order_detail"

    order_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    count = Column(Integer)
    price = Column(Integer)
