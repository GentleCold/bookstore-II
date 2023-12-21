error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "invalid order id {}",
    519: "not sufficient funds, order id {}",
    # more errors
    520: "not corresponding seller, seller id {}, order id {}",
    521: "not corresponding buyer, buyer id {}, order id {}",
    522: "not corresponding store, store id {}, order id {}",
    523: "unexpected order status, order id {}, expected status {}",
    524: "the order timeout, order id {}",
    525: "invalid key name {}",
    526: "non exist search result.",
    528: "",
}


def error_non_exist_search_result():
    return 526, error_code[526]


def error_invalid_key_name(key_name):
    return 525, error_code[525].format(key_name)


def error_order_timeout(order_id):
    return 524, error_code[524].format(order_id)


def error_unexpected_order_status(order_id, status):
    return 523, error_code[523].format(order_id, status)


def error_not_corresponding_store(store_id, order_id):
    return 522, error_code[522].format(store_id, order_id)


def error_not_corresponding_buyer(user_id, order_id):
    return 521, error_code[521].format(user_id, order_id)


def error_not_corresponding_seller(user_id, order_id):
    return 520, error_code[520].format(user_id, order_id)


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


def error_invalid_order_id(order_id):
    return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[518].format(order_id)


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message
