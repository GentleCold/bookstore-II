from typing import Optional, Tuple
from urllib.parse import urljoin

import requests


class Search:
    def __init__(self, url_prefix, token):
        self.url_prefix = urljoin(url_prefix, "search/")
        self.token = token

    def search(
        self, key: str, store_id: Optional[str], fields: Optional[list]
    ) -> Tuple[int, list]:
        json = {
            "key": key,
            "store_id": store_id,
            "fields": fields,
        }
        url = urljoin(self.url_prefix, "search")

        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("results")
