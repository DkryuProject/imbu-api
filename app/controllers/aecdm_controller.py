import httpx

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.token import get_token
from app.clients import AECDataModelClient
from app.schemas.element import ElementModel, ElementPropertyModel, CategoryRequest
from app.services.aecdm_service import AECDMService
from app.services.element import save_elements
from app.dependencies.database import get_db

router = APIRouter(prefix="/api/aec", tags=["AUTODESK AEC MODEL Interface"])


@router.get("/token", include_in_schema=False)
async def get_token(token: str = Depends(get_token)):
    return token


@router.get("/hubs")
async def get_hubs(token: str = Depends(get_token)):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    return await service.get_hubs()


@router.get("/projects/{hub_id}")
async def get_projects(hub_id: str, token: str = Depends(get_token)):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    return await service.get_projects(hub_id)


@router.get("/project/{project_id}/folders")
async def get_foldersByProject(project_id: str, token: str = Depends(get_token)):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    return await service.get_foldersByProject(project_id)


@router.get("/project/{project_id}/folders/{folder_id}")
async def get_foldersByFolder(project_id: str, folder_id: str, token: str = Depends(get_token)):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    return await service.get_foldersByFolder(project_id, folder_id)


@router.get("/project/element-groups/{project_id}")
async def get_elementGroupsByProject(project_id: str, token: str = Depends(get_token)):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    return await service.get_elementGroupsByProject(project_id)


@router.post("/category/elements/category")
async def get_elementsFromCategory(
        req: CategoryRequest,
        token: str = Depends(get_token),
        db: Session = Depends(get_db)
):
    client = AECDataModelClient(token)
    service = AECDMService(client)
    try:
        response = await service.get_elementsFromCategory(req.group_id, req.category)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="AEC API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"AEC API 호출 실패: {str(e)}")

    elements = []
    elements_group = response.get("data", {}).get("elementsByElementGroup", {})
    results = elements_group.get("results", [])

    for el in results:
        props = [
            ElementPropertyModel(
                name=p["name"],
                value=p["value"],
                displayValue=p.get("displayValue"),
                definition=p["definition"]
            )
            for p in el["properties"]["results"]
        ]
        elements.append(
            ElementModel(
                id=el.get("id", ""),
                name=el.get("name", ""),
                category=req.category,
                created_on=el.get("createdOn"),
                last_modified_on=el.get("lastModifiedOn"),
                properties=props
            )
        )

    result = save_elements(db, elements)

    return result
