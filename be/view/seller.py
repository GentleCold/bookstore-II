from flask.blueprints import Blueprint
from flask.globals import request
from flask.json import jsonify

from be.model import seller

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: int = request.json.get("stock_level", 0)

    s = seller.Seller()
    code, message = s.add_book(user_id, store_id, book_info, stock_level)

    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code


@bp_seller.route("/ship", methods=["POST"])
def ship():
    order_id: str = request.json.get("order_id")
    store_id: str = request.json.get("store_id")
    user_id: str = request.json.get("user_id")

    s = seller.Seller()
    code, message = s.ship(order_id, store_id, user_id)

    return jsonify({"message": message}), code
