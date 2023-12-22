from typing import Optional

from flask.blueprints import Blueprint
from flask.globals import request
from flask.json import jsonify

from be.model.search import Search

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/search", methods=["POST"])
def search():
    key: str = request.json.get("key")
    store_id: Optional[str] = request.json.get("store_id")
    fields: Optional[list] = request.json.get("fields")

    s = Search()
    code, message, results = s.search(key, store_id, fields)

    return jsonify({"message": message, "results": results}), code
