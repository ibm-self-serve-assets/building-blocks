"""
Patient Management Tools for Healthcare Assistant Agent

This module provides tools for retrieving and managing patient data across
different care levels (Outpatient, Inpatient, ICU, Emergency).
Based on patterns from Coffee&Me and Pulse-Bank agents.
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, List, Optional, Any


# Sample patient data - replace with your actual data source or database
PATIENT_DATA = [
    {
        "patient_id": "PAT001",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "555-0101",
        "date_of_birth": "1985-03-15",
        "care_level": "Outpatient",
        "status": "active",
        "primary_physician": "Dr. Emily Chen",
        "insurance_provider": "Blue Cross Blue Shield",
        "last_visit_date": "2026-01-15",
        "next_appointment": "2026-02-20",
        "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
        "current_medications": ["Metformin 500mg", "Lisinopril 10mg"],
        "allergies": ["Penicillin"],
        "emergency_contact": "John Johnson (555-0102)"
    },
    {
        "patient_id": "PAT002",
        "name": "Michael Chen",
        "email": "michael.chen@email.com",
        "phone": "555-0103",
        "date_of_birth": "1972-07-22",
        "care_level": "Inpatient",
        "status": "active",
        "primary_physician": "Dr. Robert Martinez",
        "insurance_provider": "Aetna",
        "admission_date": "2026-01-28",
        "room_number": "302-B",
        "diagnosis": "Pneumonia",
        "current_medications": ["Azithromycin 500mg", "Albuterol inhaler"],
        "allergies": ["None"],
        "emergency_contact": "Lisa Chen (555-0104)"
    },
    {
        "patient_id": "PAT003",
        "name": "Jennifer Williams",
        "email": "jennifer.w@email.com",
        "phone": "555-0105",
        "date_of_birth": "1990-11-08",
        "care_level": "ICU",
        "status": "critical",
        "primary_physician": "Dr. Sarah Thompson",
        "insurance_provider": "United Healthcare",
        "admission_date": "2026-02-01",
        "icu_bed": "ICU-5",
        "diagnosis": "Septic Shock",
        "current_medications": ["Norepinephrine", "Vancomycin", "Piperacillin"],
        "allergies": ["Sulfa drugs"],
        "emergency_contact": "David Williams (555-0106)"
    },
    {
        "patient_id": "PAT004",
        "name": "Robert Taylor",
        "email": "robert.taylor@email.com",
        "phone": "555-0107",
        "date_of_birth": "1965-05-30",
        "care_level": "Emergency",
        "status": "urgent",
        "primary_physician": "Dr. Emergency On-Call",
        "insurance_provider": "Medicare",
        "arrival_time": "2026-02-04 14:30",
        "triage_level": "Level 2 - Emergent",
        "chief_complaint": "Chest pain",
        "current_medications": ["Aspirin", "Nitroglycerin"],
        "allergies": ["Latex"],
        "emergency_contact": "Mary Taylor (555-0108)"
    },
    {
        "patient_id": "PAT005",
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@email.com",
        "phone": "555-0109",
        "date_of_birth": "1995-09-12",
        "care_level": "Outpatient",
        "status": "active",
        "primary_physician": "Dr. James Wilson",
        "insurance_provider": "Cigna",
        "last_visit_date": "2026-01-10",
        "next_appointment": "2026-03-15",
        "chronic_conditions": ["Asthma"],
        "current_medications": ["Albuterol inhaler", "Fluticasone"],
        "allergies": ["None"],
        "emergency_contact": "Carlos Rodriguez (555-0110)"
    },
    {
        "patient_id": "PAT006",
        "name": "David Kim",
        "email": "david.kim@email.com",
        "phone": "555-0111",
        "date_of_birth": "1978-12-25",
        "care_level": "Inpatient",
        "status": "active",
        "primary_physician": "Dr. Lisa Anderson",
        "insurance_provider": "Kaiser Permanente",
        "admission_date": "2026-01-30",
        "room_number": "405-A",
        "diagnosis": "Post-surgical recovery (Appendectomy)",
        "current_medications": ["Morphine PRN", "Cefazolin"],
        "allergies": ["Codeine"],
        "emergency_contact": "Susan Kim (555-0112)"
    },
    {
        "patient_id": "PAT007",
        "name": "Maria Garcia",
        "email": "maria.garcia@email.com",
        "phone": "555-0113",
        "date_of_birth": "1988-04-18",
        "care_level": "Outpatient",
        "status": "active",
        "primary_physician": "Dr. Michael Brown",
        "insurance_provider": "Humana",
        "last_visit_date": "2026-01-25",
        "next_appointment": "2026-02-25",
        "chronic_conditions": ["Hypothyroidism"],
        "current_medications": ["Levothyroxine 75mcg"],
        "allergies": ["Shellfish"],
        "emergency_contact": "Jose Garcia (555-0114)"
    },
    {
        "patient_id": "PAT008",
        "name": "James Anderson",
        "email": "james.anderson@email.com",
        "phone": "555-0115",
        "date_of_birth": "1955-08-07",
        "care_level": "ICU",
        "status": "critical",
        "primary_physician": "Dr. Patricia Lee",
        "insurance_provider": "Medicare",
        "admission_date": "2026-02-02",
        "icu_bed": "ICU-3",
        "diagnosis": "Acute Myocardial Infarction",
        "current_medications": ["Heparin", "Aspirin", "Atorvastatin", "Metoprolol"],
        "allergies": ["None"],
        "emergency_contact": "Barbara Anderson (555-0116)"
    }
]


@tool
def get_patient_data(
    patient_id: Optional[str] = None,
    care_level: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve patient data with flexible filtering options.
    
    Args:
        patient_id: Filter by specific patient ID
        care_level: Filter by care level (Outpatient, Inpatient, ICU, Emergency)
        status: Filter by status (e.g., 'active', 'critical', 'urgent')
        limit: Maximum number of results to return
    
    Returns:
        List of patients matching the filter criteria
    
    Example:
        >>> get_patient_data(care_level="ICU", status="critical")
        [{"patient_id": "PAT003", "name": "Jennifer Williams", ...}]
    """
    results = PATIENT_DATA.copy()
    
    # Apply filters
    if patient_id:
        results = [p for p in results if p.get("patient_id") == patient_id]
    if care_level:
        results = [p for p in results if p.get("care_level") == care_level]
    if status:
        results = [p for p in results if p.get("status") == status]
    
    # Apply limit
    if limit and limit > 0:
        results = results[:limit]
    
    return results


@tool
def get_patient_by_id(patient_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single patient by their unique identifier.
    
    Args:
        patient_id: The unique identifier for the patient (e.g., "PAT001")
    
    Returns:
        Patient data if found, None otherwise
    
    Example:
        >>> get_patient_by_id("PAT001")
        {"patient_id": "PAT001", "name": "Sarah Johnson", ...}
    """
    for patient in PATIENT_DATA:
        if patient.get("patient_id") == patient_id:
            return patient
    return None


@tool
def get_patients_by_care_level(care_level: str) -> List[Dict[str, Any]]:
    """
    Retrieve all patients in a specific care level.
    
    Args:
        care_level: The care level (Outpatient, Inpatient, ICU, Emergency)
    
    Returns:
        List of patients in the specified care level
    
    Example:
        >>> get_patients_by_care_level("ICU")
        [{"patient_id": "PAT003", ...}, {"patient_id": "PAT008", ...}]
    """
    return [p for p in PATIENT_DATA if p.get("care_level") == care_level]


@tool
def calculate_patient_metrics(
    care_level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate aggregated metrics for patients.
    
    Args:
        care_level: Optional care level to filter by
    
    Returns:
        Dictionary containing calculated metrics including:
        - total_count: Total number of patients
        - active_count: Number of active patients
        - critical_count: Number of critical patients
        - care_level_distribution: Breakdown by care level
        - status_distribution: Breakdown by status
    
    Example:
        >>> calculate_patient_metrics()
        {
            "total_count": 8,
            "active_count": 5,
            "critical_count": 2,
            "care_level_distribution": {"Outpatient": 3, "Inpatient": 2, ...}
        }
    """
    patients = PATIENT_DATA if not care_level else get_patients_by_care_level(care_level)
    
    # Calculate status counts
    active_count = len([p for p in patients if p.get("status") == "active"])
    critical_count = len([p for p in patients if p.get("status") == "critical"])
    urgent_count = len([p for p in patients if p.get("status") == "urgent"])
    
    # Calculate care level distribution
    care_levels = set(p.get("care_level") for p in patients)
    care_level_dist = {
        level: len([p for p in patients if p.get("care_level") == level])
        for level in care_levels
    }
    
    # Calculate status distribution
    statuses = set(p.get("status") for p in patients)
    status_dist = {
        status: len([p for p in patients if p.get("status") == status])
        for status in statuses
    }
    
    return {
        "total_count": len(patients),
        "active_count": active_count,
        "critical_count": critical_count,
        "urgent_count": urgent_count,
        "care_level_distribution": care_level_dist,
        "status_distribution": status_dist,
        "average_age": _calculate_average_age(patients)
    }


def _calculate_average_age(patients: List[Dict[str, Any]]) -> float:
    """Helper function to calculate average patient age."""
    from datetime import datetime
    
    ages = []
    for patient in patients:
        dob_str = patient.get("date_of_birth")
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
                age = (datetime.now() - dob).days // 365
                ages.append(age)
            except:
                continue
    
    return round(sum(ages) / len(ages), 1) if ages else 0.0