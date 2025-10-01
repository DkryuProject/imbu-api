from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship
from app.dependencies.database import engine

Base = declarative_base()


class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    element_id = Column(String, index=True, nullable=False)
    name = Column(String)
    type = Column(String)
    base_constraint = Column(String)
    top_constraint = Column(String)
    category = Column(String)
    family_name = Column(String)
    element_name = Column(String)
    revit_element_id = Column(String)
    created_on = Column(DateTime)
    last_modified_on = Column(DateTime)

    properties = relationship("ElementProperty", back_populates="element", cascade="all, delete-orphan")


class ElementProperty(Base):
    __tablename__ = "element_properties"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    element_id = Column(Integer, ForeignKey("elements.id", ondelete="CASCADE"))
    property_name = Column(String)
    property_value = Column(Text)

    element = relationship("Element", back_populates="properties")


def init_db():
    Base.metadata.create_all(bind=engine)
