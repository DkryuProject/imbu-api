import httpx

from fastapi import APIRouter, Depends, HTTPException
from app.clients import APSClient
from app.services.aps_service import APSService
from app.dependencies.token import get_token
from app.schemas.model import get_latest_version
from app.schemas.info import InfoRequest, MetadataResponse, PropertiesResponse
from app.clients import AECDataModelClient
from app.services.aecdm_service import AECDMService


router = APIRouter(prefix="/api/aps", tags=["AUTODESK APS Interface"])


@router.get("/models")
async def get_models(token: str = Depends(get_token)):
    project_id = "b.5211d789-448c-4cb6-bdc2-f56f24509f8c"
    folder_id = "urn:adsk.wipprod:fs.folder:co.03aX0nqOTYeNZ2ll7hHc6A"

    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_items(project_id, folder_id)
        items = response.get("data", [])

        models = []
        for item in items:
            itemInfo = await service.get_itemInfo(project_id, item.get("id"))
            models.append(get_latest_version(itemInfo.get("included", [])))

    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return models


@router.post("/info")
async def get_info(request: InfoRequest, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    aec_client = AECDataModelClient(token)
    aec_service = AECDMService(aec_client)

    try:
        metadata = await service.get_metadata(urn=request.urn)
        metadata_parsed = MetadataResponse(**metadata)
        guid = metadata_parsed.data.metadata[0].guid
        print("guid: ", guid)

        properties = await service.get_all_properties(urn=request.urn, guid=guid, object_id=request.dbId)
        parsed = PropertiesResponse(**properties)

        element_id_value = None
        if parsed.data.collection:
            element = parsed.data.collection[0]
            element_id_value = element.properties.get("요소 ID", {}).get("Value")
        print("element ID: ", element_id_value)

        if not element_id_value:
            return []

        group_id = "YWVjZH5ndnNTVmtQVnpsajUzTjZUOXA0SGxNX0wyQ341Yjg0OWJiNS03NDVkLTUzNWEtOWRjMS03YWM4MjM1OWRiZjQ"
        response = await aec_service.get_elementsFromElementId(group_id, element_id_value)
        result = response.get("data", {}).get("elementsByElementGroup", {}).get("results", [])

        filtered_elements = []
        for e in result:
            props_list = []
            category_type = ""
            family_name = ""
            element_name = ""
            revit_element_id = ""
            for p in e.get("properties", {}).get("results", []):
                if p["name"] == "Revit Category Type Id":
                    category_type = p.get("value")
                if p["name"] == "Family Name":
                    family_name = p.get("value")
                if p["name"] == "Element Name":
                    element_name = p.get("value")
                if p["name"] == "Revit Element ID":
                    revit_element_id = p.get("value")

                if p["definition"]["id"].startswith("parameters."):
                    props_list.append({
                        "name": p["name"],
                        "value": p.get("value")
                    })

            type_value = ""
            base = ""
            top = ""
            for p in e.get("references", {}).get("results", []):
                if p["name"] == "Type":
                    value_props = p.get("value", {}).get("properties", {}).get("results", [])
                    for r in value_props:
                        if r["name"] == "Type Comments":
                            type_value = r.get("value")
                if p["name"] == "Base Constraint":
                    base = p.get("value", {}).get("name")
                if p["name"] == "Top Constraint":
                    top = p.get("value", {}).get("name")

            filtered_elements.append({
                "id": e["id"],
                "name": e["name"],
                "type": type_value,
                "base": base,
                "top": top,
                "category_type": category_type,
                "family_name": family_name,
                "element_name": element_name,
                "revit_element_id": revit_element_id,
                "createdOn": e["createdOn"],
                "lastModifiedOn": e["lastModifiedOn"],
                "properties": props_list
            })

        print("조회된 elements:", filtered_elements)

    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return filtered_elements


@router.get("/project/{project_id}/folder/{folder_id}/items", include_in_schema=False)
async def get_itemsInFolder(project_id: str, folder_id: str, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_items(project_id, folder_id)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/project/{project_id}/item/{item_id}", include_in_schema=False)
async def get_itemInfo(project_id: str, item_id: str, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_itemInfo(project_id, item_id)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/buckets", include_in_schema=False)
async def get_buckets(token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_buckets()
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/derivative/supported-formats", include_in_schema=False)
async def get_supported_formats(token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_supported_formats()
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/derivative/{urn}/metadata")
async def get_metadata(urn: str, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_metadata(urn=urn)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/derivative/{urn}/metadata/{modelGuid}")
async def get_object_tree(urn: str, modelGuid: str, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_object_tree(urn=urn, guid=modelGuid)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/derivative/{urn}/metadata/{modelGuid}/properties")
async def get_all_properties(
        urn: str,
        modelGuid: str,
        objectid: str,
        token: str = Depends(get_token)
):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_all_properties(urn=urn, guid=modelGuid, object_id=objectid)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response


@router.get("/derivative/{urn}/manifest")
async def get_manifest(urn: str, token: str = Depends(get_token)):
    client = APSClient(token)
    service = APSService(client=client)
    try:
        response = await service.get_manifest(urn=urn)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="APS API 요청 시간 초과")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"APS API 호출 실패: {str(e)}")
    return response
