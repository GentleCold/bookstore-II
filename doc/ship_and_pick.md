## 卖家发货

**URL**

POST http://[address]/seller/ship

**Request**

Hearders:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登陆产生的会话标识 | N          |

Body:

```json
{
    "order_id": "$order id$", 
    "user_id": "$user id$", 
    "store_id": "$store id$"
}
```

| key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单ID | N          |
| user_id  | string | 用户ID | N          |
| store_id | string | 商铺ID | N          |

**Response**

Status Code:

| 码   | 描述           |
| ---- | -------------- |
| 200  | 发货成功       |
| 518  | 订单不存在     |
| 523  | 非预期订单状态 |
| 520  | 非对应卖家     |
| 522  | 非对应商店     |
| 511  | 卖家ID不存在   |
| 513  | 商店ID不存在   |

## 买家收货

**URL**

POST http://[address]/buyer/pick

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

| 码   | 描述           |
| :--- | -------------- |
| 200  | 收货成功       |
| 523  | 非预期订单状态 |
| 518  | 订单ID不存在   |
| 511  | 买家ID不存在   |
| 521  | 买家ID不匹配   |

