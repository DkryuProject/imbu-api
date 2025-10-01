import httpx
from typing import Any, Dict, Optional


class APSClient:
    def __init__(self, token: str, timeout: float = 30.0):
        self.token = token
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def _request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers or self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        return await self._request("GET", url, params=params, headers=headers)

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        return await self._request("POST", url, data=data, json=json, headers=headers)

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        return await self._request("PUT", url, data=data, json=json, headers=headers)

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None):
        return await self._request("DELETE", url, headers=headers)
