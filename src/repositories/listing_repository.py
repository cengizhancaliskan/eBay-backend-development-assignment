from typing import Any

from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exceptions import DatabaseError, ValidationError
from src.models.listing import (
    BooleanPropertyValue,
    DatasetEntity,
    Listing,
    Property,
    StringPropertyValue,
    listing_entity_association,
)
from src.schemas.listing import (
    EntityCreateOrUpdateSchema,
    ListingCreateOrUpdateSchema,
    ListingFilterSchema,
    PropertyCreateOrUpdateSchema,
)


class ListingRepository:
    def __init__(self, db_session: AsyncSession, page_size: int = 100):
        self._session = db_session
        self.default_page_size = page_size

    async def fetch_listings(self, filters: ListingFilterSchema) -> list[Listing]:
        try:
            # Build base query with eager loading
            stmt = select(Listing).options(
                joinedload(Listing.string_properties).joinedload(
                    StringPropertyValue.property
                ),
                joinedload(Listing.boolean_properties).joinedload(
                    BooleanPropertyValue.property
                ),
                selectinload(Listing.entities),
            )

            stmt = self.apply_filters(stmt, filters)

            page_size = self.default_page_size
            if filters.page_size:
                page_size = filters.page_size

            # Apply pagination
            offset = (filters.page - 1) * page_size
            stmt = stmt.order_by(Listing.listing_id).offset(offset).limit(page_size)

            # Execute query
            result = await self._session.execute(stmt)
            listings = result.scalars().unique().all()

            return list(listings)

        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving listings: {str(e)}")

    async def upsert_listing(
        self, listing_data: ListingCreateOrUpdateSchema
    ) -> tuple[Listing, bool]:
        try:
            stmt = (
                select(Listing)
                .options(joinedload(Listing.entities))
                .where(Listing.listing_id == listing_data.listing_id)
            )
            result = await self._session.execute(stmt)
            existing_listing = result.scalars().unique().one_or_none()
            is_new = existing_listing is None

            if existing_listing:
                await self._update_listing(existing_listing, listing_data)
            else:
                existing_listing = await self._create_listing(listing_data)

            await self._update_properties(existing_listing, listing_data.properties)
            await self._update_entities(existing_listing, listing_data.entities)

            try:
                await self._session.commit()
            except IntegrityError:
                await self._session.rollback()
                raise

            return existing_listing, is_new
        except ValidationError as e:
            raise e
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseError(f"Error upserting listing: {str(e)}")

    async def count_total_listings(self, filters: ListingFilterSchema) -> int:
        stmt = select(func.count(Listing.listing_id))

        stmt = self.apply_filters(stmt, filters)

        return await self._session.scalar(stmt) or 0

    @staticmethod
    def apply_filters(stmt: Select[Any], filters: ListingFilterSchema) -> Select[Any]:
        if filters.listing_id:
            stmt = stmt.filter(Listing.listing_id == filters.listing_id)

        if filters.scan_date_from:
            stmt = stmt.filter(Listing.scan_date >= filters.scan_date_from)

        if filters.scan_date_to:
            stmt = stmt.filter(Listing.scan_date <= filters.scan_date_to)

        if filters.is_active is not None:
            stmt = stmt.filter(Listing.is_active == filters.is_active)

        if filters.image_hashes:
            stmt = stmt.filter(
                Listing.image_hashes.op("@>")(array(filters.image_hashes))
            )

        if filters.dataset_entities:
            for key, val in filters.dataset_entities.items():
                stmt = stmt.join(Listing.entities).filter(
                    DatasetEntity.data[key].op("->>")(key) == str(val)
                )

        if filters.property_filters:
            for property_id, expected_value in filters.property_filters.items():
                stmt = (
                    stmt.join(Listing.string_properties)  # type: ignore
                    .join(StringPropertyValue.property)
                    .filter(
                        and_(
                            Property.property_id == property_id,
                            StringPropertyValue.value == str(expected_value),
                        )
                    )
                    .union(
                        stmt.join(Listing.boolean_properties)
                        .join(BooleanPropertyValue.property)
                        .filter(
                            and_(
                                Property.property_id == property_id,
                                BooleanPropertyValue.value == bool(expected_value),
                            )
                        )
                    )
                )
        return stmt

    async def _create_listing(self, data: ListingCreateOrUpdateSchema) -> Listing:
        try:
            listing = Listing(
                listing_id=data.listing_id,
                scan_date=data.scan_date.replace(tzinfo=None),
                is_active=data.is_active,
                image_hashes=data.image_hashes,
                dataset_entity_ids=[],
            )
            self._session.add(listing)

            await self._session.flush()
            await self._session.refresh(listing)

            return listing
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error creating listing: {str(e)}")

    async def _update_listing(
        self, listing: Listing, data: ListingCreateOrUpdateSchema
    ) -> None:
        listing.scan_date = data.scan_date
        listing.is_active = data.is_active
        listing.image_hashes = data.image_hashes

    async def _update_properties(
        self, listing: Listing, properties: list[PropertyCreateOrUpdateSchema]
    ) -> None:
        if len(properties) == 0:
            return
        try:
            # Delete existing property associations
            delete_stmt = delete(StringPropertyValue).where(
                StringPropertyValue.listing_id == listing.listing_id
            )
            await self._session.execute(delete_stmt)

            delete_stmt = delete(BooleanPropertyValue).where(
                BooleanPropertyValue.listing_id == listing.listing_id
            )
            await self._session.execute(delete_stmt)

            for prop in properties:
                stmt = select(Property).where(
                    Property.name == prop.name, Property.type == prop.type
                )
                result = await self._session.execute(stmt)
                property_obj = result.scalar_one_or_none()

                # Create property if it doesn't exist
                if not property_obj:
                    property_obj = Property(name=prop.name, type=prop.type)
                    self._session.add(property_obj)
                    await self._session.flush()  # Flush to get the property ID

                if property_obj.type == "str":
                    property_val_obj_stmt = select(StringPropertyValue).where(
                        StringPropertyValue.property_id == property_obj.property_id,
                        StringPropertyValue.listing_id == listing.listing_id,
                    )
                    new_prop_val_obj = StringPropertyValue(
                        listing_id=listing.listing_id,
                        property_id=property_obj.property_id,
                        value=prop.value,
                    )
                elif property_obj.type == "bool":
                    property_val_obj_stmt = select(BooleanPropertyValue).where(
                        BooleanPropertyValue.property_id == property_obj.property_id,
                        BooleanPropertyValue.listing_id == listing.listing_id,
                    )  # type: ignore
                    new_prop_val_obj = BooleanPropertyValue(
                        listing_id=listing.listing_id,
                        property_id=property_obj.property_id,
                        value=prop.value,
                    )  # type: ignore
                else:
                    raise ValidationError(f"Invalid property type: {property_obj.type}")
                property_val_obj_result = await self._session.execute(
                    property_val_obj_stmt
                )
                prop_val_obj = property_val_obj_result.scalar_one_or_none()
                if not prop_val_obj:
                    self._session.add(new_prop_val_obj)
                else:
                    prop_val_obj.value = str(prop.value)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error updating properties: {str(e)}")

    async def _update_entities(
        self, listing: Listing, entities: list[EntityCreateOrUpdateSchema]
    ) -> None:
        if len(entities) == 0:
            return
        try:
            # Delete existing entity associations
            delete_stmt = delete(listing_entity_association).where(
                listing_entity_association.c.listing_id == listing.listing_id
            )
            await self._session.execute(delete_stmt)

            # Clear existing relationships
            new_entity_ids = []
            listing.entities = []
            is_listing_changed = False

            for entity in entities:
                stmt = select(DatasetEntity).where(DatasetEntity.name == entity.name)
                result = await self._session.execute(stmt)
                entity_obj = result.scalar_one_or_none()

                if not entity_obj:
                    entity_obj = DatasetEntity(name=entity.name, data=entity.data)
                    self._session.add(entity_obj)
                    await self._session.flush()

                # Append the entity to the listing's entities relationship and dataset_entity_ids list
                if entity_obj not in listing.entities:
                    is_listing_changed = True
                    listing.entities.append(entity_obj)

                if entity_obj.entity_id not in new_entity_ids:
                    is_listing_changed = True
                    new_entity_ids.append(entity_obj.entity_id)

            listing.dataset_entity_ids = new_entity_ids
            if is_listing_changed:
                await self._session.flush()

        except SQLAlchemyError as e:
            raise DatabaseError(f"Error updating entity references: {str(e)}")
