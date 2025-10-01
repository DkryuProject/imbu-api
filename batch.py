import asyncio
from app.dependencies.token import get_token
from app.dependencies.database import get_db
from app.clients import AECDataModelClient
from app.services.aecdm_service import AECDMService
from app.schemas.element import ElementModel, ElementPropertyModel
from app.services.element import save_elements


async def get_elements():
    group_id = "YWVjZH5ndnNTVmtQVnpsajUzTjZUOXA0SGxNX0wyQ341Yjg0OWJiNS03NDVkLTUzNWEtOWRjMS03YWM4MjM1OWRiZjQ"
    category = "Walls"

    db = next(get_db())
    try:
        token = await get_token(db)
        print("토큰:", token)
    finally:
        db.close()

    client = AECDataModelClient(token)
    service = AECDMService(client)

    response = await service.get_elementsFromCategory(group_id, category)
    print(response.get("data", {}).get("elementsByElementGroup", {}).get("totalCount"))

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

    elements = []
    for el in filtered_elements:
        props = [
            ElementPropertyModel(
                name=p["name"],
                value=p["value"],
            )
            for p in el["properties"]
        ]
        elements.append(
            ElementModel(
                element_id=el.get("id", ""),
                name=el.get("name", ""),
                type=el.get("type", ""),
                base_constraint=el.get("base", ""),
                top_constraint=el.get("top", ""),
                category=el.get("category_type", ""),
                family_name=el.get("family_name", ""),
                element_name=el.get("element_name", ""),
                revit_element_id=el.get("revit_element_id", ""),
                created_on=el.get("createdOn"),
                last_modified_on=el.get("lastModifiedOn"),
                properties=props
            )
        )

    result = save_elements(db, elements)
    print("result:", result)

if __name__ == "__main__":
    asyncio.run(get_elements())
