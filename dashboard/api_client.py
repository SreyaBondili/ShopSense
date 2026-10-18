import requests
from typing import Optional, Dict, Any, List

class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if response.status_code >= 400:
            error_msg = data.get("detail", f"Request failed with status {response.status_code}")
            if isinstance(error_msg, list):
                error_msg = "\n".join(str(m) for m in error_msg)
            elif isinstance(error_msg, dict):
                error_msg = str(error_msg)
            raise Exception(error_msg)

        return data

    # 1. Auth APIs
    def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        resp = requests.post(url, json={"email": email, "password": password})
        return self._handle_response(resp)

    def register(
        self,
        full_name: str,
        email: str,
        password: str,
        role: str,
        admin_secret: Optional[str] = None,
        phone: Optional[str] = None,
        business_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/register"
        payload = {
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": role
        }
        if admin_secret:
            payload["admin_secret"] = admin_secret
        if phone:
            payload["phone"] = phone
        if business_name:
            payload["business_name"] = business_name
        if category:
            payload["category"] = category
        resp = requests.post(url, json=payload)
        return self._handle_response(resp)

    def get_me(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/me"
        resp = requests.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 2. Analytics APIs
    def get_summary(self, token: str, vendor_id: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/analytics/summary"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_vendor_performance(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/vendor-performance"
        resp = requests.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_product_performance(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/product-performance"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_revenue_trend(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/revenue-trend"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_category_performance(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/category-performance"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    # 3. Vendor APIs
    def get_vendors(
        self,
        token: str,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/vendors"
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def create_vendor(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors"
        resp = requests.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_vendor(self, token: str, vendor_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors/{vendor_id}"
        resp = requests.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def delete_vendor(self, token: str, vendor_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors/{vendor_id}"
        resp = requests.delete(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 4. Product APIs
    def get_products(
        self,
        token: str,
        vendor_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/products"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        if category and category != "All":
            params["category"] = category
        if search:
            params["search"] = search
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def create_product(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products"
        resp = requests.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_product(self, token: str, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products/{product_id}"
        resp = requests.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def delete_product(self, token: str, product_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products/{product_id}"
        resp = requests.delete(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 5. Inventory APIs
    def get_inventory(self, token: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/inventory"
        params = {}
        if status and status != "All":
            params["status"] = status
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def update_inventory(self, token: str, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/inventory/{product_id}"
        resp = requests.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    # 6. Transaction APIs
    def get_transactions(
        self,
        token: str,
        vendor_id: Optional[int] = None,
        product_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/transactions"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        if product_id:
            params["product_id"] = product_id
        resp = requests.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def create_transaction(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/transactions"
        resp = requests.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)
