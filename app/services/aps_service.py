from app.clients import APSClient

FIND_FOLDERS_ITEMS = '/data/v1/projects/{project_id}/folders/{folder_id}/contents?filter[type]=items'
GET_FILE = '/data/v1/projects/{project_id}/items/{item_id}'
GET_BUCKETS = '/oss/v2/buckets'
GET_SUPPORTED_FORMATS = '/formats'
GET_METADATA = '/{urn}/metadata'
GET_OBJECT_TREE = '/{urn}/metadata/{guid}'
GET_ALL_PROPERTIES = '/{urn}/metadata/{guid}/properties'
GET_MANIFEST = '/{urn}/manifest'


class APSService:
    def __init__(self, client: APSClient):
        self.client = client

    async def get_items(self, project_id, folder_id):
        url = "https://developer.api.autodesk.com" + FIND_FOLDERS_ITEMS.format(project_id=project_id, folder_id=folder_id)
        return await self.client.get(url)

    async def get_itemInfo(self, project_id, item_id):
        url = "https://developer.api.autodesk.com" + GET_FILE.format(project_id=project_id, item_id=item_id)
        return await self.client.get(url)

    async def get_buckets(self):
        url = "https://developer.api.autodesk.com" + GET_BUCKETS
        return await self.client.get(url)

    async def get_supported_formats(self):
        url = "https://developer.api.autodesk.com/modelderivative/v2/designdata" + GET_SUPPORTED_FORMATS
        return await self.client.get(url)

    async def get_metadata(self, urn):
        url = "https://developer.api.autodesk.com/modelderivative/v2/designdata" + GET_METADATA.format(urn=urn)
        return await self.client.get(url)

    async def get_object_tree(self, urn, guid):
        url = "https://developer.api.autodesk.com/modelderivative/v2/designdata" + GET_OBJECT_TREE.format(urn=urn, guid=guid)
        return await self.client.get(url)

    async def get_all_properties(self, urn, guid, object_id):
        url = "https://developer.api.autodesk.com/modelderivative/v2/designdata" + GET_ALL_PROPERTIES.format(urn=urn, guid=guid)
        params = {"objectid": object_id}
        return await self.client.get(url, params=params)

    async def get_manifest(self, urn):
        url = "https://developer.api.autodesk.com/modelderivative/v2/designdata" + GET_MANIFEST.format(urn=urn)
        return await self.client.get(url)
