from sqlalchemy import Column, Float, Integer, String, Text, text
from sqlalchemy.orm import declarative_base
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType

# from sqlalchemy.orm import relationship

Base = declarative_base()
make_searchable(Base.metadata)


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
