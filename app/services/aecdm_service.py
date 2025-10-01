import yaml
from pathlib import Path
from app.clients import AECDataModelClient
from app.schemas import HubSchema, ProjectSchema, FolderSchema


class AECDMService:
    def __init__(self, client: AECDataModelClient, query_file: str = "app/clients/queries.yaml"):
        self.client = client
        self.queries = self.load_queries(query_file)

    @staticmethod
    def load_queries(file_path):
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    async def get_hubs(self):
        response = await self.client.query(self.queries["GET_HUBS"])
        results = response.get("data", {}).get("hubs", {}).get("results", [])
        return [HubSchema(**hub) for hub in results]

    async def get_projects(self, hub_id):
        variables = {"hubId": hub_id}
        response = await self.client.query(self.queries["GET_PROJECTS"], variables)
        results = response.get("data", {}).get("projects", {}).get("results", [])
        projects = [ProjectSchema(**proj) for proj in results if isinstance(proj, dict)]
        return projects

    async def get_foldersByProject(self, project_id):
        variables = {"projectId": project_id}
        response = await self.client.query(self.queries["GET_FOLDERS_BY_PROJECT"], variables)
        results = response.get("data", {}).get("foldersByProject", {}).get("results", [])
        projects = [FolderSchema(**folder) for folder in results if isinstance(folder, dict)]
        return projects

    async def get_foldersByFolder(self, project_id, folder_id):
        variables = {"projectId": project_id, "folderId": folder_id}
        response = await self.client.query(self.queries["GET_FOLDERS_BY_FOLDER"], variables)
        results = response.get("data", {}).get("foldersByFolder", {}).get("results", [])
        projects = [FolderSchema(**folder) for folder in results if isinstance(folder, dict)]
        return projects

    async def get_elementGroupsByProject(self, project_id):
        variables = {"projectId": project_id}
        return await self.client.query(self.queries["GET_ELEMENT_GROUPS_BY_PROJECT"], variables)

    async def get_elementsFromCategory(self, group_id, category):
        variables = {
            "elementGroupId": group_id,
            "propertyFilter": f"'property.name.Revit Category Type Id'=='{category}'"
        }
        return await self.client.query(self.queries["GET_ELEMENTS_FROM_CATEGORY"], variables)

    async def get_elementsFromElementId(self, group_id, element_id):
        variables = {
            "elementGroupId": group_id,
            "propertyFilter": f"'property.name.Revit Element ID'=={element_id}"
        }
        return await self.client.query(self.queries["GET_ELEMENTS_FROM_CATEGORY"], variables)