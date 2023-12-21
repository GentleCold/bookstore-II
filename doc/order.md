## 买家查询历史订单

**URL**

POST http://[address]/buyer/look_up_order

**Request**

Hearders:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登陆产生的会话标识 | N          |

Body:

```json
{ 
    "user_id": "$user id$"
}
```

| key     | 类型   | 描述   | 是否可为空 |
| ------- | ------ | ------ | ---------- |
| user_id | string | 用户ID | N          |

**Response**

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 查询成功     |
| 511  | 用户ID不存在 |

Body:

```json
{ 
    "results": [
        "order_id": "$order_id$",
        "store_id": "$store_id$",
        "state": "$state$",
        "time": "$order_time$",
        "books": [{
        	"book_id": "$book_id$",
        	"count": "$count$",
        	"price": "$price$"
        }]
    ]
}
```

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| order_id | string | 订单ID     | N          |
| store_id | string | 商店ID     | N          |
| state    | int    | 状态       | N          |
| time     | float  | 下单时间戳 | N          |
| book_id  | string | 图书ID     | N          |
| count    | int    | 图书数量   | N          |
| price    | int    | 图书价格   | N          |

## 买家取消订单

**URL**

POST http://[address]/buyer/cancel_order

**Request**

Hearders:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登陆产生的会话标识 | N          |

Body:

```json
{
    "user_id": "$user id$"
    "order_id": "$order id$"
}
```

| key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单ID | N          |
| user_id  | string | 买家ID | N          |

**Response**

Status Code:

| 码   | 描述         |
| :--- | ------------ |
| 200  | 订单取消成功 |
| 518  | 订单ID不存在 |
| 511  | 买家ID不存在 |
| 521  | 买家ID不匹配 |