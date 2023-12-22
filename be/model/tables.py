from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType

Base = declarative_base()
make_searchable(Base.metadata)


class UserTable(Base):
    __tablename__ = "user_table"

    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    balance = Column(Integer)
    token = Column(String, nullable=True)
    terminal = Column(String, nullable=True)


class StoreTable(Base):
    __tablename__ = "store_table"

    store_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_table.user_id"))

    user = relationship("UserTable", backref="stores")


class OrderTable(Base):
    __tablename__ = "order_table"

    order_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_table.user_id"))
    store_id = Column(String, ForeignKey("store_table.store_id"))
    state = Column(Integer)
    time = Column(Float)

    user = relationship("UserTable", backref="orders")
    store = relationship("StoreTable", backref="orders")


class StoreBookTable(Base):
    __tablename__ = "store_book_table"

    store_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    price = Column(Integer)
    stock_level = Column(Integer, CheckConstraint("stock_level >= 0"))


class OrderDetailTable(Base):
    __tablename__ = "order_detail_table"

    order_id = Column(String, primary_key=True)
    book_id = Column(String, primary_key=True)
    count = Column(Integer)
    price = Column(Integer)


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
]


class BookTable(Base):
    __tablename__ = "book_table"
    store_id = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    original_title = Column(String)
    translator = Column(String)
    pub_year = Column(String)
    pages = Column(Integer)
    binding = Column(String)
    isbn = Column(String)
    author_intro = Column(Text)
    book_intro = Column(Text)
    tags = Column(String)
    currency_unit = Column(String)

    search_vector = Column(TSVectorType(*allowed_fields))
