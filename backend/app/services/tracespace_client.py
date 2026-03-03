"""Trace.Space API client for integration."""

import httpx
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import Parameter


class TraceSpaceClient:
    """Client for Trace.Space API integration."""

    def __init__(self, client_id: str, client_secret: str, org: str):
        """Initialize Trace.Space client.

        Args:
            client_id: Trace.Space client ID
            client_secret: Trace.Space client secret
            org: Organization slug
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.org = org
        self.base_url = "https://app.tracespace.io/api"
        self.token: Optional[str] = None

    async def authenticate(self) -> bool:
        """Authenticate with Trace.Space and get access token.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/token",
                    json={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    return True
        except Exception:
            pass
        return False

    async def get_items(self) -> Optional[list]:
        """Fetch items from Trace.Space.

        Returns:
            List of items or None if request fails
        """
        if not self.token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orgs/{self.org}/items",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return None

    async def get_item_fields(self, item_id: str) -> Optional[list]:
        """Fetch fields for a specific item.

        Args:
            item_id: Trace.Space item ID

        Returns:
            List of fields or None if request fails
        """
        if not self.token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orgs/{self.org}/items/{item_id}/fields",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return None

    async def get_field_value(self, item_id: str, field_name: str) -> Optional[Any]:
        """Get the value of a specific field.

        Args:
            item_id: Trace.Space item ID
            field_name: Field name

        Returns:
            Field value or None if not found
        """
        fields = await self.get_item_fields(item_id)
        if fields:
            for field in fields:
                if field.get("name") == field_name:
                    return field.get("value")
        return None

    async def sync_parameter(
        self, parameter: Parameter, db: Session
    ) -> bool:
        """Sync a parameter value with Trace.Space.

        Fetches the current value from Trace.Space and updates the parameter.

        Args:
            parameter: Parameter to sync
            db: Database session

        Returns:
            True if sync successful, False otherwise
        """
        if not parameter.tracespace_field_name or not parameter.item.tracespace_item_id:
            return False

        value = await self.get_field_value(
            parameter.item.tracespace_item_id, parameter.tracespace_field_name
        )

        if value is not None:
            try:
                parameter.value = float(value)
                db.commit()
                return True
            except Exception:
                pass

        return False

    async def push_parameter(
        self, parameter: Parameter, db: Session
    ) -> bool:
        """Push a parameter value to Trace.Space.

        Updates the field in Trace.Space with the current parameter value.

        Args:
            parameter: Parameter to push
            db: Database session

        Returns:
            True if push successful, False otherwise
        """
        if not parameter.tracespace_field_name or not parameter.item.tracespace_item_id:
            return False

        if not self.token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/orgs/{self.org}/items/{parameter.item.tracespace_item_id}/fields/{parameter.tracespace_field_name}",
                    json={"value": parameter.value},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                return response.status_code == 200
        except Exception:
            pass

        return False
