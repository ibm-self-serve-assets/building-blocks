"""
Data Processing Utilities
Transforms IBM Concert API responses into formats suitable for visualization
Handles actual API field structures with flexible field matching
"""

import logging
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes IBM Concert API data for visualization
    Implements flexible field matching with fallbacks for actual API structures
    """
    
    @staticmethod
    def calculate_severity(risk_score: float) -> str:
        """
        Calculate CVE severity from risk score
        
        Args:
            risk_score: Risk score value (0-10)
            
        Returns:
            Severity level string
        """
        if risk_score >= 9.0:
            return 'CRITICAL'
        elif risk_score >= 7.0:
            return 'HIGH'
        elif risk_score >= 4.0:
            return 'MEDIUM'
        elif risk_score > 0:
            return 'LOW'
        else:
            return 'INFORMATIONAL'
    
    @staticmethod
    def get_severity_color(severity: str) -> str:
        """
        Get color code for severity level
        
        Args:
            severity: Severity level string
            
        Returns:
            Hex color code
        """
        colors = {
            'CRITICAL': '#721c24',
            'HIGH': '#dc3545',
            'MEDIUM': '#ffc107',
            'LOW': '#17a2b8',
            'INFORMATIONAL': '#6c757d'
        }
        return colors.get(severity, '#6c757d')
    
    @staticmethod
    def format_timestamp(timestamp: Any) -> str:
        """
        Convert UNIX timestamp to formatted date string
        
        Args:
            timestamp: UNIX timestamp (int or float) or None
            
        Returns:
            Formatted date string or 'N/A'
        """
        if timestamp is None or timestamp == 0:
            return 'N/A'
        
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime('%Y-%m-%d')
            return str(timestamp)
        except Exception as e:
            logger.warning(f"Failed to format timestamp {timestamp}: {str(e)}")
            return 'N/A'
    
    @staticmethod
    def parse_json_metadata(metadata_str: Optional[str]) -> Dict[str, Any]:
        """
        Parse JSON metadata string
        
        Args:
            metadata_str: JSON string or None
            
        Returns:
            Parsed dictionary or empty dict
        """
        if not metadata_str:
            return {}
        
        try:
            return json.loads(metadata_str)
        except Exception as e:
            logger.warning(f"Failed to parse metadata: {str(e)}")
            return {}
    
    @staticmethod
    def process_cves(cves: List[Dict]) -> pd.DataFrame:
        """
        Process CVE data into DataFrame with actual field mappings
        
        Args:
            cves: List of CVE dictionaries from API
            
        Returns:
            Processed DataFrame
        """
        if not cves:
            logger.warning("No CVEs to process")
            return pd.DataFrame()
        
        # Log sample structure for debugging
        if cves:
            logger.debug(f"Sample CVE structure: {list(cves[0].keys())}")
        
        processed = []
        for cve in cves:
            # Extract fields with fallbacks
            cve_id = cve.get('cve', cve.get('cve_id', 'N/A'))
            risk_score = cve.get('highest_finding_risk_score', cve.get('risk_score', 0))
            
            # Calculate severity
            severity = DataProcessor.calculate_severity(risk_score)
            
            # Extract description
            description = (
                cve.get('wx_details') or 
                cve.get('wx_recommendation') or 
                cve.get('description') or 
                'No description available'
            )
            
            # Extract other fields
            priority = cve.get('highest_finding_priority', cve.get('priority', 'N/A'))
            state = cve.get('state', 'N/A')
            total_findings = cve.get('total_findings', 0)
            
            # Count related CVEs
            related_cves = cve.get('related_cves', [])
            related_count = len(related_cves) if related_cves else 0
            
            processed.append({
                'CVE ID': cve_id,
                'Severity': severity,
                'Risk Score': risk_score,
                'Description': description[:100] + '...' if len(description) > 100 else description,
                'Priority': priority,
                'State': state,
                'Findings': total_findings,
                'Related': related_count
            })
        
        df = pd.DataFrame(processed)
        logger.info(f"Processed {len(df)} CVEs")
        return df
    
    @staticmethod
    def process_applications(applications: List[Dict]) -> pd.DataFrame:
        """
        Process application data into DataFrame with actual field mappings
        
        Args:
            applications: List of application dictionaries from API
            
        Returns:
            Processed DataFrame
        """
        if not applications:
            logger.warning("No applications to process")
            return pd.DataFrame()
        
        # Log sample structure for debugging
        if applications:
            logger.debug(f"Sample application structure: {list(applications[0].keys())}")
        
        processed = []
        for app in applications:
            # Extract fields with fallbacks
            name = app.get('name', 'N/A')
            version = app.get('version', 'N/A')
            status = app.get('resilience_status', app.get('status', 'N/A'))
            
            # Format timestamp
            last_updated = DataProcessor.format_timestamp(
                app.get('last_updated_on', app.get('last_updated'))
            )
            
            # Extract owner
            owner = app.get('last_updated_by', app.get('owner', 'N/A'))
            
            # Extract vulnerability count
            vuln_count = app.get('criticality', app.get('vulnerability_count', 0))
            
            # Check for build artifacts
            associations = app.get('associations', {})
            has_artifacts = 'Yes' if associations.get('build_artifacts') else 'No'
            
            processed.append({
                'Name': name,
                'Version': version,
                'Status': status,
                'Vulnerabilities': vuln_count,
                'Last Updated': last_updated,
                'Owner': owner,
                'Has Artifacts': has_artifacts
            })
        
        df = pd.DataFrame(processed)
        logger.info(f"Processed {len(df)} applications")
        return df
    
    @staticmethod
    def process_certificates(certificates: List[Dict]) -> pd.DataFrame:
        """
        Process certificate data into DataFrame with actual field mappings
        
        Args:
            certificates: List of certificate dictionaries from API
            
        Returns:
            Processed DataFrame
        """
        if not certificates:
            logger.warning("No certificates to process")
            return pd.DataFrame()
        
        # Log sample structure for debugging
        if certificates:
            logger.debug(f"Sample certificate structure: {list(certificates[0].keys())}")
        
        processed = []
        for cert in certificates:
            # Extract fields with fallbacks
            cert_id = cert.get('id', cert.get('certificate_id', 'N/A'))
            subject = cert.get('subject', cert.get('common_name', 'N/A'))
            issuer = cert.get('issuer', 'N/A')
            serial = cert.get('serial_number', 'N/A')
            status = cert.get('status', 'N/A')
            
            # Format timestamps
            valid_from = DataProcessor.format_timestamp(
                cert.get('validity_start_date', cert.get('valid_from'))
            )
            valid_to = DataProcessor.format_timestamp(
                cert.get('validity_end_date', cert.get('valid_to'))
            )
            
            # Parse metadata
            metadata = DataProcessor.parse_json_metadata(cert.get('metadata'))
            algorithm = metadata.get('hash_algorithm', 'N/A')
            key_size = metadata.get('public_key_length', 'N/A')
            
            # Calculate days until expiry
            days_to_expiry = 'N/A'
            try:
                expiry_timestamp = cert.get('validity_end_date', cert.get('valid_to'))
                if expiry_timestamp:
                    expiry_date = datetime.fromtimestamp(expiry_timestamp)
                    days = (expiry_date - datetime.now()).days
                    days_to_expiry = days
            except Exception as e:
                logger.debug(f"Could not calculate days to expiry: {str(e)}")
            
            processed.append({
                'ID': cert_id,
                'Subject': subject,
                'Issuer': issuer,
                'Serial Number': serial,
                'Status': status,
                'Valid From': valid_from,
                'Valid To': valid_to,
                'Days to Expiry': days_to_expiry,
                'Algorithm': algorithm,
                'Key Size': key_size
            })
        
        df = pd.DataFrame(processed)
        logger.info(f"Processed {len(df)} certificates")
        return df
    
    @staticmethod
    def process_build_artifacts(artifacts: List[Dict]) -> pd.DataFrame:
        """
        Process build artifact data into DataFrame
        
        Args:
            artifacts: List of build artifact dictionaries from API
            
        Returns:
            Processed DataFrame
        """
        if not artifacts:
            logger.warning("No build artifacts to process")
            return pd.DataFrame()
        
        # Log sample structure for debugging
        if artifacts:
            logger.debug(f"Sample artifact structure: {list(artifacts[0].keys())}")
        
        processed = []
        for artifact in artifacts:
            # Extract fields with fallbacks
            artifact_id = artifact.get('id', 'N/A')
            name = artifact.get('name', 'N/A')
            version = artifact.get('version', 'N/A')
            artifact_type = artifact.get('type', 'N/A')
            
            # Format timestamp
            created = DataProcessor.format_timestamp(
                artifact.get('created_on', artifact.get('created_at'))
            )
            
            # Extract vulnerability count if available
            vuln_count = artifact.get('vulnerability_count', 0)
            
            processed.append({
                'ID': artifact_id,
                'Name': name,
                'Version': version,
                'Type': artifact_type,
                'Created': created,
                'Vulnerabilities': vuln_count
            })
        
        df = pd.DataFrame(processed)
        logger.info(f"Processed {len(df)} build artifacts")
        return df
    
    @staticmethod
    def get_severity_distribution(df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculate severity distribution from CVE DataFrame
        
        Args:
            df: DataFrame with 'Severity' column
            
        Returns:
            Dictionary with severity counts
        """
        if df.empty or 'Severity' not in df.columns:
            return {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'INFORMATIONAL': 0
            }
        
        distribution = df['Severity'].value_counts().to_dict()
        
        # Ensure all severity levels are present
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL']:
            if severity not in distribution:
                distribution[severity] = 0
        
        return distribution
    
    @staticmethod
    def get_priority_distribution(df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculate priority distribution from CVE DataFrame
        
        Args:
            df: DataFrame with 'Priority' column
            
        Returns:
            Dictionary with priority counts
        """
        if df.empty or 'Priority' not in df.columns:
            return {}
        
        # Filter out N/A and empty priorities
        valid_priorities = df[df['Priority'].notna() & (df['Priority'] != 'N/A') & (df['Priority'] != '')]
        
        if valid_priorities.empty:
            return {}
        
        return valid_priorities['Priority'].value_counts().to_dict()

# Made with Bob
