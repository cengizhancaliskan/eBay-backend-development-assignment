from datetime import datetime
from typing import List

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Listing(BaseModel):
    __tablename__ = BaseModel.get_table_name("listings")

    listing_id: Mapped[str] = mapped_column(String, primary_key=True)
    scan_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    dataset_entity_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    image_hashes: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    # Relationships
    string_properties = relationship("StringPropertyValue", back_populates="listing")
    boolean_properties = relationship("BooleanPropertyValue", back_populates="listing")


class Property(BaseModel):
    __tablename__ = BaseModel.get_table_name("properties")

    property_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    string_values = relationship("StringPropertyValue", back_populates="property")
    boolean_values = relationship("BooleanPropertyValue", back_populates="property")


class StringPropertyValue(BaseModel):
    __tablename__ = BaseModel.get_table_name("property_values_str")

    listing_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(BaseModel.get_table_name("listings") + ".listing_id"),
        primary_key=True
    )
    property_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(BaseModel.get_table_name("properties") + ".property_id"),
        primary_key=True
    )
    value: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    listing = relationship("Listing", back_populates="string_properties")
    property = relationship("Property", back_populates="string_values")


class BooleanPropertyValue(BaseModel):
    __tablename__ = BaseModel.get_table_name("property_values_bool")

    listing_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(BaseModel.get_table_name("listings") + ".listing_id"),
        primary_key=True
    )
    property_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(BaseModel.get_table_name("properties") + ".property_id"),
        primary_key=True
    )
    value: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    listing = relationship("Listing", back_populates="boolean_properties")
    property = relationship("Property", back_populates="boolean_values")


class DatasetEntity(BaseModel):
    __tablename__ = BaseModel.get_table_name("dataset_entities")

    entity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
