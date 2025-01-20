from src.models.listing import Listing
from src.repositories.listing_repository import ListingRepository
from src.schemas.listing import (
    EntitySchema,
    ListingCreateOrUpdateResponse,
    ListingFilterSchema,
    ListingResponse,
    ListingResponseSchema,
    ListingsCreateOrUpdateSchema,
    PropertySchema,
)


class ListingService:
    def __init__(self, listing_repository: ListingRepository):
        self._repository = listing_repository

    async def get_listings(self, filters: ListingFilterSchema) -> ListingResponse:
        listings = await self._repository.fetch_listings(filters)
        total_count = await self._repository.count_total_listings(filters)

        listings_map = []
        for listing in listings:
            properties = self._get_properties(listing)
            entities = self._get_entities(listing)

            listings_map.append(
                ListingResponseSchema(
                    listing_id=listing.listing_id,
                    scan_date=listing.scan_date,
                    is_active=listing.is_active,
                    dataset_entity_ids=listing.dataset_entity_ids,
                    image_hashes=listing.image_hashes,
                    properties=properties,
                    entities=entities,
                )
            )

        return ListingResponse(listings=listings_map, total=total_count)

    async def create_or_update_listings(
        self, data: ListingsCreateOrUpdateSchema
    ) -> ListingCreateOrUpdateResponse:
        created_count = 0
        updated_count = 0
        errors = []

        try:
            for listing_data in data.listings:
                try:
                    listing, is_new = await self._repository.upsert_listing(
                        listing_data
                    )
                    if is_new:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(
                        f"Error processing listing: #{listing_data.listing_id}: {str(e)}"
                    )

            return ListingCreateOrUpdateResponse(
                success=len(errors) == 0,
                message=(
                    "Listings processed successfully"
                    if not errors
                    else "Some listings failed to process"
                ),
                created_count=created_count,
                updated_count=updated_count,
                errors=errors if errors else None,
            )
        except Exception as e:
            raise e

    @staticmethod
    def _get_properties(listing: Listing) -> list[PropertySchema]:
        properties = []
        for sp in listing.string_properties:
            properties.append(
                PropertySchema(name=sp.property.name, type="str", value=sp.value)
            )
        for bp in listing.boolean_properties:
            properties.append(
                PropertySchema(name=bp.property.name, type="bool", value=bp.value)
            )
        return properties

    # @staticmethod
    def _get_entities(self, listing: Listing) -> list[EntitySchema]:
        entities: list[EntitySchema] = []

        for entity in listing.entities:
            entities.append(EntitySchema(name=entity.name, data=entity.data))

        return entities
