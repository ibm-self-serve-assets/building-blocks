"""
IBM Concert REST API Client
Handles all API interactions with proper authentication and error handling
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONCERT_BASE_URL, C_API_KEY, INSTANCE_ID, API_TIMEOUT, API_PAGE_LIMIT

logger = logging.getLogger(__name__)


class ConcertAPIClient:
    """
    Client for interacting with IBM Concert REST APIs
    Implements proper authentication, pagination handling, and error management
    """
    
    def __init__(self):
        """Initialize the Concert API client with configuration"""
        self.base_url = CONCERT_BASE_URL.rstrip('/')
        self.api_key = C_API_KEY
        self.instance_id = INSTANCE_ID
        self.timeout = API_TIMEOUT
        self.page_limit = API_PAGE_LIMIT
        
        logger.info("ConcertAPIClient initialized")
        logger.debug(f"Base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers for API requests
        Uses C_API_KEY format (literal prefix) and InstanceID header
        """
        return {
            'authorization': f'C_API_KEY {self.api_key}',
            'InstanceID': self.instance_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP GET request to Concert API with error handling
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: For various API errors with descriptive messages
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        logger.info(f"Making request to: {endpoint}")
        logger.debug(f"Full URL: {url}")
        logger.debug(f"Parameters: {params}")
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle specific error codes
            if response.status_code == 401:
                error_msg = "Authentication failed. Check C_API_KEY."
                logger.error(error_msg)
                raise Exception(error_msg)
            
            elif response.status_code == 403:
                error_msg = "Access forbidden. Check INSTANCE_ID."
                logger.error(error_msg)
                raise Exception(error_msg)
            
            elif response.status_code == 404:
                error_msg = f"Resource not found: {endpoint}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            elif response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
        
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout: {endpoint}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except requests.exceptions.ConnectionError:
            error_msg = "Network connection error. Check CONCERT_BASE_URL."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            if "Authentication failed" in str(e) or "Access forbidden" in str(e) or "Resource not found" in str(e):
                raise
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
    
    def _extract_data(self, response: Dict[str, Any], data_fields: List[str]) -> List[Dict]:
        """
        Extract data array from paginated response
        Tries multiple field names in priority order
        
        Args:
            response: API response dictionary
            data_fields: List of possible data field names to try
            
        Returns:
            List of data items
        """
        for field in data_fields:
            if field in response:
                data = response[field]
                logger.debug(f"Extracted {len(data)} items from '{field}' field")
                return data
        
        logger.warning(f"No data field found. Tried: {data_fields}")
        return []
    
    # CVE Endpoints
    
    def get_cves(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all CVEs from Concert API
        
        Args:
            limit: Maximum number of CVEs to retrieve
            
        Returns:
            List of CVE dictionaries
        """
        endpoint = '/core/api/v1/vulnerability/cves'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            cves = self._extract_data(response, ['cves', 'data', 'items'])
            logger.info(f"Retrieved {len(cves)} CVEs")
            return cves
        except Exception as e:
            logger.error(f"Failed to get CVEs: {str(e)}")
            raise
    
    # Application Endpoints
    
    def get_applications(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all applications from Concert API
        
        Args:
            limit: Maximum number of applications to retrieve
            
        Returns:
            List of application dictionaries
        """
        endpoint = '/core/api/v1/applications'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            apps = self._extract_data(response, ['applications', 'data', 'items'])
            logger.info(f"Retrieved {len(apps)} applications")
            return apps
        except Exception as e:
            logger.error(f"Failed to get applications: {str(e)}")
            raise
    
    def get_application_details(self, app_name: str) -> Dict:
        """
        Get details for a specific application
        
        Args:
            app_name: Application name (will be URL-encoded)
            
        Returns:
            Application details dictionary
        """
        encoded_name = quote(app_name, safe='')
        endpoint = f'/core/api/v1/applications/{encoded_name}'
        
        try:
            response = self._make_request(endpoint)
            logger.info(f"Retrieved details for application: {app_name}")
            return response
        except Exception as e:
            logger.error(f"Failed to get application details for {app_name}: {str(e)}")
            raise
    
    def get_application_vulnerabilities(self, app_name: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get vulnerability details for a specific application
        
        Args:
            app_name: Application name (will be URL-encoded)
            limit: Maximum number of vulnerabilities to retrieve
            
        Returns:
            List of vulnerability detail dictionaries
        """
        encoded_name = quote(app_name, safe='')
        endpoint = f'/core/api/v1/applications/{encoded_name}/vulnerability_details'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            vulns = self._extract_data(response, ['vulnerability_details', 'vulnerabilities', 'data', 'items'])
            logger.info(f"Retrieved {len(vulns)} vulnerabilities for application: {app_name}")
            return vulns
        except Exception as e:
            logger.error(f"Failed to get vulnerabilities for {app_name}: {str(e)}")
            raise
    
    def get_build_artifacts(self, app_name: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get build artifacts for a specific application
        
        Args:
            app_name: Application name (will be URL-encoded)
            limit: Maximum number of artifacts to retrieve
            
        Returns:
            List of build artifact dictionaries
        """
        encoded_name = quote(app_name, safe='')
        endpoint = f'/core/api/v1/applications/{encoded_name}/build_artifacts'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            artifacts = self._extract_data(response, ['build_artifacts', 'data', 'items'])
            logger.info(f"Retrieved {len(artifacts)} build artifacts for application: {app_name}")
            return artifacts
        except Exception as e:
            logger.error(f"Failed to get build artifacts for {app_name}: {str(e)}")
            raise
    
    def get_build_artifact_cves(self, app_name: str, artifact_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get CVEs for a specific build artifact
        
        Args:
            app_name: Application name (will be URL-encoded)
            artifact_id: Build artifact ID
            limit: Maximum number of CVEs to retrieve
            
        Returns:
            List of CVE dictionaries for the artifact
        """
        encoded_name = quote(app_name, safe='')
        endpoint = f'/core/api/v1/applications/{encoded_name}/build_artifacts/{artifact_id}/cves'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            cves = self._extract_data(response, ['cves', 'data', 'items'])
            logger.info(f"Retrieved {len(cves)} CVEs for artifact {artifact_id} of application: {app_name}")
            return cves
        except Exception as e:
            logger.error(f"Failed to get CVEs for artifact {artifact_id} of {app_name}: {str(e)}")
            raise
    
    # Certificate Endpoints
    
    def get_certificates(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all certificates from Concert API
        
        Args:
            limit: Maximum number of certificates to retrieve
            
        Returns:
            List of certificate dictionaries
        """
        endpoint = '/core/api/v1/certificates'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            certs = self._extract_data(response, ['certificates', 'data', 'items'])
            logger.info(f"Retrieved {len(certs)} certificates")
            return certs
        except Exception as e:
            logger.error(f"Failed to get certificates: {str(e)}")
            raise
    
    def get_certificate_details(self, cert_id: str) -> Dict:
        """
        Get details for a specific certificate
        
        Args:
            cert_id: Certificate ID
            
        Returns:
            Certificate details dictionary
        """
        endpoint = f'/core/api/v1/certificates/{cert_id}'
        
        try:
            response = self._make_request(endpoint)
            logger.info(f"Retrieved details for certificate: {cert_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get certificate details for {cert_id}: {str(e)}")
            raise
    
    def get_certificate_issuers(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all certificate issuers from Concert API
        
        Args:
            limit: Maximum number of issuers to retrieve
            
        Returns:
            List of issuer dictionaries
        """
        endpoint = '/core/api/v1/certificate_issuers'
        params = {'limit': limit or self.page_limit}
        
        try:
            response = self._make_request(endpoint, params)
            issuers = self._extract_data(response, ['issuers', 'data', 'items'])
            logger.info(f"Retrieved {len(issuers)} certificate issuers")
            return issuers
        except Exception as e:
            logger.error(f"Failed to get certificate issuers: {str(e)}")
            raise

# Made with Bob
