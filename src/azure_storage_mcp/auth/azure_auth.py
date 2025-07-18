"""Azure authentication manager for MCP server."""

import re
from typing import Optional, Union

from azure.identity import (
    AzureCliCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ClientSecretCredential,
)
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ClientAuthenticationError

from ..utils.exceptions import AuthenticationError, ValidationError
from ..utils.logging import StructuredLogger


class AzureAuthManager:
    """Manages Azure authentication for the MCP server."""
    
    def __init__(self, auth_method: str = "default") -> None:
        self.auth_method = auth_method
        self._credential: Optional[TokenCredential] = None
        self.logger = StructuredLogger(__name__)
    
    async def get_credential(self) -> TokenCredential:
        """Get Azure credential based on configured auth method."""
        if self._credential is None:
            self._credential = self._create_credential()
        return self._credential
    
    def _create_credential(self) -> TokenCredential:
        """Create credential based on auth method."""
        try:
            if self.auth_method == "default":
                credential = DefaultAzureCredential()
            elif self.auth_method == "cli":
                credential = AzureCliCredential()
            elif self.auth_method == "managed_identity":
                credential = ManagedIdentityCredential()
            elif self.auth_method == "service_principal":
                credential = self._create_service_principal_credential()
            else:
                raise AuthenticationError(
                    f"Unknown authentication method: {self.auth_method}",
                    self.auth_method
                )
            
            self.logger.log_authentication(self.auth_method, True)
            return credential
            
        except Exception as e:
            self.logger.log_authentication(self.auth_method, False, str(e))
            raise AuthenticationError(
                f"Failed to create credential for method {self.auth_method}: {str(e)}",
                self.auth_method
            )
    
    def _create_service_principal_credential(self) -> ClientSecretCredential:
        """Create service principal credential from environment variables."""
        import os
        
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        
        if not all([tenant_id, client_id, client_secret]):
            raise AuthenticationError(
                "Service principal authentication requires AZURE_TENANT_ID, "
                "AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET environment variables",
                "service_principal"
            )
        
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    
    async def test_authentication(self) -> bool:
        """Test if authentication is working by getting a token."""
        try:
            credential = await self.get_credential()
            # Test by getting a token for the management scope
            token = credential.get_token("https://management.azure.com/.default")
            return token is not None
        except ClientAuthenticationError as e:
            self.logger.log_authentication(self.auth_method, False, str(e))
            return False
        except Exception as e:
            self.logger.log_error(e, {"context": "test_authentication"})
            return False


class SecurityValidator:
    """Validates Azure resource identifiers and parameters."""
    
    @staticmethod
    def validate_subscription_id(subscription_id: str) -> str:
        """Validate Azure subscription ID format."""
        if not subscription_id:
            raise ValidationError("Subscription ID cannot be empty", "subscription_id")
        
        # UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, subscription_id.lower()):
            raise ValidationError(
                "Invalid subscription ID format. Must be a valid UUID",
                "subscription_id"
            )
        
        return subscription_id
    
    @staticmethod
    def validate_resource_group(resource_group: str) -> str:
        """Validate Azure resource group name."""
        if not resource_group:
            raise ValidationError("Resource group name cannot be empty", "resource_group")
        
        # Azure resource group name validation
        # Must be 1-90 characters, alphanumeric, periods, underscores, hyphens
        if not re.match(r'^[a-zA-Z0-9._-]+$', resource_group):
            raise ValidationError(
                "Invalid resource group name. Must contain only alphanumeric characters, "
                "periods, underscores, and hyphens",
                "resource_group"
            )
        
        if len(resource_group) > 90:
            raise ValidationError(
                "Resource group name cannot exceed 90 characters",
                "resource_group"
            )
        
        return resource_group
    
    @staticmethod
    def validate_storage_account_name(account_name: str) -> str:
        """Validate Azure storage account name."""
        if not account_name:
            raise ValidationError("Storage account name cannot be empty", "account_name")
        
        # Azure storage account name validation
        # Must be 3-24 characters, lowercase letters and numbers only
        if not re.match(r'^[a-z0-9]+$', account_name):
            raise ValidationError(
                "Invalid storage account name. Must contain only lowercase letters and numbers",
                "account_name"
            )
        
        if len(account_name) < 3 or len(account_name) > 24:
            raise ValidationError(
                "Storage account name must be between 3 and 24 characters",
                "account_name"
            )
        
        return account_name