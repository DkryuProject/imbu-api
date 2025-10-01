import httpx

AEC_GRAPHQL_URL = "https://developer.api.autodesk.com/aec/graphql"


class AECDataModelClient:
    def __init__(self, token: str):
        self.token = token

    async def query(self, graphql_query: str, variables=None):
        payload = {"query": graphql_query}
        if variables is not None:
            payload["variables"] = variables

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                AEC_GRAPHQL_URL,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            resp.raise_for_status()
            return resp.json()
