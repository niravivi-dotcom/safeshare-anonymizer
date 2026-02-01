"""
Crypto Handler Module
Handles encryption and decryption of mapping files
"""

import json
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
from loguru import logger


class CryptoHandler:
    """Handles encryption/decryption of sensitive mapping files"""
    
    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Salt bytes
            
        Returns:
            Derived key
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_mapping(mapping: Dict[str, Any], password: str,
                       output_path: Path) -> None:
        """
        Encrypt mapping dictionary to file
        
        Args:
            mapping: Dictionary to encrypt
            password: Encryption password
            output_path: Path to save encrypted file
            
        Raises:
            ValueError: If encryption fails
        """
        try:
            logger.info("Encrypting mapping file...")
            
            # Generate random salt
            import os
            salt = os.urandom(16)
            
            # Derive key from password
            key = CryptoHandler._derive_key(password, salt)
            fernet = Fernet(key)
            
            # Convert mapping to JSON
            json_data = json.dumps(mapping, ensure_ascii=False, indent=2)
            
            # Encrypt
            encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
            
            # Save salt + encrypted data
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(salt + encrypted_data)
            
            logger.success(f"Mapping encrypted and saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"לא ניתן להצפין את קובץ המיפוי: {str(e)}")
    
    @staticmethod
    def decrypt_mapping(encrypted_path: Path, password: str) -> Dict[str, Any]:
        """
        Decrypt mapping file
        
        Args:
            encrypted_path: Path to encrypted file
            password: Decryption password
            
        Returns:
            Decrypted mapping dictionary
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            logger.info("Decrypting mapping file...")
            
            # Read file
            with open(encrypted_path, 'rb') as f:
                data = f.read()
            
            # Extract salt and encrypted data
            salt = data[:16]
            encrypted_data = data[16:]
            
            # Derive key
            key = CryptoHandler._derive_key(password, salt)
            fernet = Fernet(key)
            
            # Decrypt
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Parse JSON
            mapping = json.loads(decrypted_data.decode('utf-8'))
            
            logger.success("Mapping decrypted successfully")
            return mapping
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"לא ניתן לפענח את קובץ המיפוי: {str(e)}")
    
    @staticmethod
    def save_mapping_json(mapping: Dict[str, Any], output_path: Path) -> None:
        """
        Save mapping as plain JSON (for testing/debugging only!)
        WARNING: Not secure - use encrypt_mapping for production
        
        Args:
            mapping: Dictionary to save
            output_path: Path to save JSON file
        """
        logger.warning("Saving UNENCRYPTED mapping file - use only for testing!")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Mapping saved to: {output_path}")


# TODO: Future enhancements
# - Add support for multiple encryption algorithms
# - Add key rotation functionality
# - Add secure key storage (keyring integration)
# - Add mapping file versioning
