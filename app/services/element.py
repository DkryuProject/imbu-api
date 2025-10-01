from sqlalchemy.orm import Session
from app.models.element import Element, ElementProperty
from app.schemas.element import ElementModel


def save_elements(db: Session, elements: list[ElementModel]):
    for el in elements:
        element = Element(
            element_id=el.element_id,
            name=el.name,
            type=el.type,
            base_constraint=el.base_constraint,
            top_constraint=el.top_constraint,
            category=el.category,
            family_name=el.family_name,
            element_name=el.element_name,
            revit_element_id=el.revit_element_id,
            created_on=el.created_on,
            last_modified_on=el.last_modified_on
        )
        db.add(element)
        db.flush()

        for prop in el.properties:
            db_prop = ElementProperty(
                element_id=element.id,
                property_name=prop.property_name,
                property_value=prop.property_value,
            )
            db.add(db_prop)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"저장 실패, error={e}")

    return {"status": "success"}

