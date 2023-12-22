## 搜索图书

#### URL

POST http://[address]/search/search

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

##### Body:

```json
{
  "store_id": "$store id$",
  "key": "$key$",
  "fields": ["title", "tags", ...],
}
```

| key      | 类型         | 描述                                                                           | 是否可为空 |
| -------- | ------------ | ------------------------------------------------------------------------------ | ---------- |
| store_id | string       | 搜索店名（如果为空则为全站搜索）                                               | Y          |
| keys     | string       | 搜索的关键字                                                                   | N          |
| fields   | list[string] | 搜索的字段范围，如果为空则不限制搜索字段，否则只搜索这些字段，字段间是或的关系 | Y          |

#### Response

Status Code:

| 码  | 描述                 |
| --- | -------------------- |
| 200 | 搜索成功             |
| 5XX | 搜索结果为空         |
| 5XX | 店铺不存在           |
| 5XX | 限制的字段名称不存在 |

##### Body:

```json
[
  {
    "store_id": "$store id$",
    "book_id": "$book id$",
    "book_info": "$book info$",
    "pictures": "$pictures$",
    "stock_level": "stock_level"
  }
]
```

##### 属性说明：

| 变量名      | 类型   | 描述                | 是否可为空 |
| ----------- | ------ | ------------------- | ---------- |
| store_id    | string | 商铺ID              | N          |
| book_id     | string | 书本ID              | N          |
| book_info   | class  | 书籍信息            | N          |
| pictures    | list   | 书籍图片            | N          |
| stock_level | int    | 初始库存，大于等于0 | N          |
