"""
Vault Client Module
Handles all interactions with HashiCorp Vault
"""

import hvac
import base64
from typing import Dict, Optional, Any


class VaultClient:
    """Vault client wrapper for secret management operations"""

    def __init__(self, vault_addr: str, vault_token: str):
        """
        Initialize Vault client
        
        Args:
            vault_addr: Vault server address (e.g., http://127.0.0.1:8200)
            vault_token: Vault authentication token
        """
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the hvac client"""
        try:
            self.client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token
            )
        except Exception as e:
            print(f"Error initializing Vault client: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """
        Check if Vault client is connected and authenticated
        
        Returns:
            bool: True if connected and authenticated, False otherwise
        """
        if not self.client:
            return False
        
        try:
            return self.client.is_authenticated()
        except Exception:
            return False

    def get_health(self) -> Dict[str, Any]:
        """
        Get Vault health status
        
        Returns:
            dict: Health status information
        """
        try:
            return self.client.sys.read_health_status()
        except Exception as e:
            return {"error": str(e)}

    def enable_kv_v2_engine(self, mount_point: str = "secret") -> bool:
        """
        Enable KV v2 secrets engine
        
        Args:
            mount_point: Mount point for the KV engine
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if already enabled
            mounts = self.client.sys.list_mounted_secrets_engines()
            if f"{mount_point}/" in mounts:
                return True
            
            # Enable KV v2
            self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path=mount_point,
                options={'version': '2'}
            )
            return True
        except Exception as e:
            print(f"Error enabling KV v2 engine: {e}")
            return False

    def enable_transit_engine(self, mount_point: str = "transit") -> bool:
        """
        Enable Transit secrets engine
        
        Args:
            mount_point: Mount point for the Transit engine
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if already enabled
            mounts = self.client.sys.list_mounted_secrets_engines()
            if f"{mount_point}/" in mounts:
                return True
            
            # Enable Transit
            self.client.sys.enable_secrets_engine(
                backend_type='transit',
                path=mount_point
            )
            return True
        except Exception as e:
            print(f"Error enabling Transit engine: {e}")
            return False

    def create_transit_key(self, key_name: str, key_type: str = "aes256-gcm96") -> bool:
        """
        Create a Transit encryption key
        
        Args:
            key_name: Name of the encryption key
            key_type: Type of key (aes256-gcm96, rsa-2048, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if key already exists
            try:
                self.client.secrets.transit.read_key(name=key_name)
                return True
            except hvac.exceptions.InvalidPath:
                pass
            
            # Create key
            self.client.secrets.transit.create_key(
                name=key_name,
                key_type=key_type
            )
            return True
        except Exception as e:
            print(f"Error creating Transit key: {e}")
            return False

    def transit_encrypt(self, key_name: str, plaintext: str) -> Optional[str]:
        """
        Encrypt data using Transit engine
        
        Args:
            key_name: Name of the encryption key
            plaintext: Data to encrypt
            
        Returns:
            str: Encrypted ciphertext or None if failed
        """
        try:
            # Encode plaintext to base64
            plaintext_b64 = base64.b64encode(plaintext.encode()).decode()
            
            # Encrypt
            response = self.client.secrets.transit.encrypt_data(
                name=key_name,
                plaintext=plaintext_b64
            )
            
            return response['data']['ciphertext']
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return None

    def transit_decrypt(self, key_name: str, ciphertext: str) -> Optional[str]:
        """
        Decrypt data using Transit engine
        
        Args:
            key_name: Name of the encryption key
            ciphertext: Data to decrypt
            
        Returns:
            str: Decrypted plaintext or None if failed
        """
        try:
            # Decrypt
            response = self.client.secrets.transit.decrypt_data(
                name=key_name,
                ciphertext=ciphertext
            )
            
            # Decode from base64
            plaintext_b64 = response['data']['plaintext']
            plaintext = base64.b64decode(plaintext_b64).decode()
            
            return plaintext
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None

    def kv_write_secret(self, path: str, secret_data: Dict[str, Any]) -> bool:
        """
        Write secret to KV v2 store
        
        Args:
            path: Secret path (without mount point)
            secret_data: Secret data dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure KV v2 is enabled
            self.enable_kv_v2_engine()
            
            # Write secret
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_data
            )
            return True
        except Exception as e:
            print(f"Error writing secret to KV: {e}")
            return False

    def kv_read_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Read secret from KV v2 store
        
        Args:
            path: Secret path (without mount point)
            
        Returns:
            dict: Secret data or None if failed
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            print(f"Error reading secret from KV: {e}")
            return None

    def kv_delete_secret(self, path: str) -> bool:
        """
        Delete secret from KV v2 store (soft delete)
        
        Args:
            path: Secret path (without mount point)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.secrets.kv.v2.delete_latest_version_of_secret(path=path)
            return True
        except Exception as e:
            print(f"Error deleting secret from KV: {e}")
            return False

    def kv_list_secrets(self, path: str = "") -> Optional[list]:
        """
        List secrets at a given path
        
        Args:
            path: Path to list (without mount point)
            
        Returns:
            list: List of secret names or None if failed
        """
        try:
            response = self.client.secrets.kv.v2.list_secrets(path=path)
            return response['data']['keys']
        except Exception as e:
            print(f"Error listing secrets: {e}")
            return None

# Made with Bob
