"""
Communication Generation Tools for Healthcare Assistant Agent

This module provides tools for generating personalized healthcare communications
including appointment confirmations, lab alerts, medication reminders, wellness tips,
and billing notices.

IMPORTANT:
- Data is EMBEDDED directly in this tool as Python dicts
- This tool does NOT call other tools (tools run in isolation in WXO)
- This tool does NOT load from CSV files (WXO cannot access local files)
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, Optional, Any, List
from datetime import datetime


# Embedded patient data — WXO tools CANNOT access local CSV files
# Each tool must have its own copy of the data it needs
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
def generate_patient_communication(
    patient_id: str,
    communication_type: str,
    additional_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate personalized healthcare communications for patients.
    
    Args:
        patient_id: The patient's unique identifier
        communication_type: Type of communication (appointment_confirmation, lab_result_alert,
                          medication_reminder, wellness_tip, billing_notice)
        additional_context: Optional additional information to include
    
    Returns:
        Dictionary containing the generated communication with subject, body, and metadata
    
    Example:
        >>> generate_patient_communication("PAT001", "appointment_confirmation")
        {
            "subject": "Appointment Confirmation - February 20, 2026",
            "body": "<html>...",
            "patient_id": "PAT001",
            "communication_type": "appointment_confirmation"
        }
    """
    # Look up patient from embedded data (NOT from CSV, NOT from other tools)
    patient = None
    for p in PATIENT_DATA:
        if p.get('patient_id') == patient_id:
            patient = p
            break
    
    if not patient:
        return {
            "error": f"Patient {patient_id} not found",
            "patient_id": patient_id
        }
    
    # Get the appropriate template
    template_func = _get_communication_template(communication_type)
    if not template_func:
        return {
            "error": f"Unknown communication type: {communication_type}",
            "patient_id": patient_id
        }
    
    # Generate the communication
    communication = template_func(patient, additional_context)
    
    # Add metadata
    communication["patient_id"] = patient_id
    communication["patient_name"] = patient.get("name")
    communication["care_level"] = patient.get("care_level")
    communication["communication_type"] = communication_type
    communication["generated_at"] = datetime.now().isoformat()
    
    return communication


def _get_communication_template(communication_type: str):
    """Get the appropriate template function for the communication type."""
    templates = {
        "appointment_confirmation": _generate_appointment_confirmation,
        "lab_result_alert": _generate_lab_result_alert,
        "medication_reminder": _generate_medication_reminder,
        "wellness_tip": _generate_wellness_tip,
        "billing_notice": _generate_billing_notice
    }
    return templates.get(communication_type)


def _generate_appointment_confirmation(patient: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
    """Generate appointment confirmation communication."""
    name = patient.get("name", "Patient")
    care_level = patient.get("care_level", "Outpatient")
    physician = patient.get("primary_physician", "Your physician")
    next_appt = patient.get("next_appointment", "TBD")
    
    # Care level specific styling
    priority_class = _get_priority_class(care_level)
    
    subject = f"Appointment Confirmation - {next_appt}"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .appointment-box {{ background-color: white; border-left: 4px solid {priority_class['color']}; padding: 15px; margin: 20px 0; }}
            .care-level {{ display: inline-block; background-color: {priority_class['color']}; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
            .button {{ background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            .important {{ color: #d9534f; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Healthcare Assistant</h1>
            <p>Your Health, Our Priority</p>
        </div>
        
        <div class="content">
            <h2>Hello {name},</h2>
            
            <p>This confirms your upcoming appointment:</p>
            
            <div class="appointment-box">
                <p><strong>Date:</strong> {next_appt}</p>
                <p><strong>Provider:</strong> {physician}</p>
                <p><strong>Care Level:</strong> <span class="care-level">{care_level}</span></p>
                {f'<p><strong>Additional Information:</strong> {context}</p>' if context else ''}
            </div>
            
            <h3>Before Your Appointment:</h3>
            <ul>
                <li>Arrive 15 minutes early for check-in</li>
                <li>Bring your insurance card and photo ID</li>
                <li>Bring a list of current medications</li>
                <li>Prepare any questions for your provider</li>
            </ul>
            
            {_get_care_level_instructions(care_level)}
            
            <p>Need to reschedule? Contact us at least 24 hours in advance.</p>
            
            <a href="#" class="button">Manage Appointment</a>
        </div>
        
        <div class="footer">
            <p>Healthcare Assistant Agent | Available 24/7</p>
            <p>For urgent matters, call 911 or visit the nearest emergency room</p>
        </div>
    </body>
    </html>
    """
    
    return {"subject": subject, "body": body, "priority": priority_class['priority']}


def _generate_lab_result_alert(patient: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
    """Generate lab result alert communication."""
    name = patient.get("name", "Patient")
    care_level = patient.get("care_level", "Outpatient")
    physician = patient.get("primary_physician", "Your physician")
    
    priority_class = _get_priority_class(care_level)
    
    subject = "Lab Results Available"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .result-box {{ background-color: white; border-left: 4px solid {priority_class['color']}; padding: 15px; margin: 20px 0; }}
            .care-level {{ display: inline-block; background-color: {priority_class['color']}; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
            .button {{ background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Healthcare Assistant</h1>
            <p>Your Health, Our Priority</p>
        </div>
        
        <div class="content">
            <h2>Hello {name},</h2>
            
            <p>Your recent lab results are now available for review.</p>
            
            <div class="result-box">
                <p><strong>Care Level:</strong> <span class="care-level">{care_level}</span></p>
                <p><strong>Ordering Provider:</strong> {physician}</p>
                {f'<p><strong>Results Summary:</strong> {context}</p>' if context else ''}
            </div>
            
            <h3>Next Steps:</h3>
            <ul>
                <li>Review your results in the patient portal</li>
                <li>Your provider will contact you if action is needed</li>
                <li>Schedule a follow-up if recommended</li>
            </ul>
            
            <a href="#" class="button">View Results</a>
            
            <p><em>Note: These results have been reviewed by your healthcare team.</em></p>
        </div>
        
        <div class="footer">
            <p>Healthcare Assistant Agent | Available 24/7</p>
            <p>For urgent concerns, contact your provider immediately</p>
        </div>
    </body>
    </html>
    """
    
    return {"subject": subject, "body": body, "priority": priority_class['priority']}


def _generate_medication_reminder(patient: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
    """Generate medication reminder communication."""
    name = patient.get("name", "Patient")
    care_level = patient.get("care_level", "Outpatient")
    medications = patient.get("current_medications", [])
    
    priority_class = _get_priority_class(care_level)
    
    subject = "Medication Refill Reminder"
    
    med_list = "".join([f"<li>{med}</li>" for med in medications]) if medications else "<li>No medications on file</li>"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .med-box {{ background-color: white; border-left: 4px solid {priority_class['color']}; padding: 15px; margin: 20px 0; }}
            .care-level {{ display: inline-block; background-color: {priority_class['color']}; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
            .button {{ background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Healthcare Assistant</h1>
            <p>Your Health, Our Priority</p>
        </div>
        
        <div class="content">
            <h2>Hello {name},</h2>
            
            <p>This is a reminder about your medications:</p>
            
            <div class="med-box">
                <p><strong>Care Level:</strong> <span class="care-level">{care_level}</span></p>
                <h3>Current Medications:</h3>
                <ul>
                    {med_list}
                </ul>
                {f'<p><strong>Note:</strong> {context}</p>' if context else ''}
            </div>
            
            <h3>Medication Management Tips:</h3>
            <ul>
                <li>Take medications as prescribed</li>
                <li>Request refills before running out</li>
                <li>Report any side effects to your provider</li>
                <li>Keep an updated medication list</li>
            </ul>
            
            <a href="#" class="button">Request Refill</a>
        </div>
        
        <div class="footer">
            <p>Healthcare Assistant Agent | Available 24/7</p>
            <p>For medication questions, contact your pharmacist or provider</p>
        </div>
    </body>
    </html>
    """
    
    return {"subject": subject, "body": body, "priority": priority_class['priority']}


def _generate_wellness_tip(patient: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
    """Generate wellness tip communication."""
    name = patient.get("name", "Patient")
    care_level = patient.get("care_level", "Outpatient")
    conditions = patient.get("chronic_conditions", [])
    
    priority_class = _get_priority_class(care_level)
    
    subject = "Your Personalized Wellness Tip"
    
    # Customize tip based on conditions
    wellness_content = context if context else _get_wellness_content(conditions, care_level)
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .wellness-box {{ background-color: white; border-left: 4px solid {priority_class['color']}; padding: 15px; margin: 20px 0; }}
            .care-level {{ display: inline-block; background-color: {priority_class['color']}; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Healthcare Assistant</h1>
            <p>Your Health, Our Priority</p>
        </div>
        
        <div class="content">
            <h2>Hello {name},</h2>
            
            <p>Here's your personalized wellness tip:</p>
            
            <div class="wellness-box">
                <p><strong>Care Level:</strong> <span class="care-level">{care_level}</span></p>
                {wellness_content}
            </div>
            
            <p><em>Remember: Small steps lead to big health improvements!</em></p>
        </div>
        
        <div class="footer">
            <p>Healthcare Assistant Agent | Available 24/7</p>
            <p>Consult your provider before making significant health changes</p>
        </div>
    </body>
    </html>
    """
    
    return {"subject": subject, "body": body, "priority": "normal"}


def _generate_billing_notice(patient: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
    """Generate billing notice communication."""
    name = patient.get("name", "Patient")
    care_level = patient.get("care_level", "Outpatient")
    insurance = patient.get("insurance_provider", "Your insurance")
    
    priority_class = _get_priority_class(care_level)
    
    subject = "Billing Statement Available"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .billing-box {{ background-color: white; border-left: 4px solid {priority_class['color']}; padding: 15px; margin: 20px 0; }}
            .care-level {{ display: inline-block; background-color: {priority_class['color']}; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
            .button {{ background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Healthcare Assistant</h1>
            <p>Your Health, Our Priority</p>
        </div>
        
        <div class="content">
            <h2>Hello {name},</h2>
            
            <p>Your billing statement is now available for review.</p>
            
            <div class="billing-box">
                <p><strong>Care Level:</strong> <span class="care-level">{care_level}</span></p>
                <p><strong>Insurance:</strong> {insurance}</p>
                {f'<p><strong>Details:</strong> {context}</p>' if context else ''}
            </div>
            
            <h3>Payment Options:</h3>
            <ul>
                <li>Pay online through the patient portal</li>
                <li>Set up a payment plan if needed</li>
                <li>Contact billing with questions</li>
                <li>Review insurance coverage details</li>
            </ul>
            
            <a href="#" class="button">View Statement</a>
            <a href="#" class="button">Make Payment</a>
            
            <p><em>Questions about your bill? Our billing team is here to help.</em></p>
        </div>
        
        <div class="footer">
            <p>Healthcare Assistant Agent | Available 24/7</p>
            <p>Billing inquiries: billing@healthcare.com | (555) 123-4567</p>
        </div>
    </body>
    </html>
    """
    
    return {"subject": subject, "body": body, "priority": "normal"}


def _get_priority_class(care_level: str) -> Dict[str, str]:
    """Get styling based on care level priority."""
    priorities = {
        "Emergency": {"color": "#d9534f", "priority": "urgent"},
        "ICU": {"color": "#f0ad4e", "priority": "high"},
        "Inpatient": {"color": "#5bc0de", "priority": "medium"},
        "Outpatient": {"color": "#5cb85c", "priority": "normal"}
    }
    return priorities.get(care_level, {"color": "#5cb85c", "priority": "normal"})


def _get_care_level_instructions(care_level: str) -> str:
    """Get care level specific instructions."""
    instructions = {
        "Emergency": "<p class='important'>⚠️ For emergency appointments, please arrive immediately.</p>",
        "ICU": "<p class='important'>⚠️ ICU visits require advance coordination with nursing staff.</p>",
        "Inpatient": "<p><strong>Note:</strong> Hospital-based appointments may require additional check-in procedures.</p>",
        "Outpatient": "<p><strong>Note:</strong> Please complete any required pre-visit forms online.</p>"
    }
    return instructions.get(care_level, "")


def _get_wellness_content(conditions: list, care_level: str) -> str:
    """Generate personalized wellness content based on conditions."""
    if "Diabetes" in str(conditions):
        return """
        <h3>Managing Blood Sugar Levels</h3>
        <p>Regular monitoring and healthy eating are key to diabetes management:</p>
        <ul>
            <li>Check blood sugar as recommended by your provider</li>
            <li>Choose whole grains and limit refined carbohydrates</li>
            <li>Stay physically active - aim for 30 minutes daily</li>
            <li>Stay hydrated with water</li>
        </ul>
        """
    elif "Hypertension" in str(conditions):
        return """
        <h3>Heart-Healthy Living</h3>
        <p>Small lifestyle changes can make a big difference:</p>
        <ul>
            <li>Reduce sodium intake to less than 2,300mg daily</li>
            <li>Exercise regularly - even walking helps!</li>
            <li>Manage stress through relaxation techniques</li>
            <li>Monitor your blood pressure at home</li>
        </ul>
        """
    elif "Asthma" in str(conditions):
        return """
        <h3>Breathing Easy with Asthma</h3>
        <p>Keep your asthma under control:</p>
        <ul>
            <li>Use your controller medication daily as prescribed</li>
            <li>Avoid known triggers (smoke, allergens, cold air)</li>
            <li>Keep your rescue inhaler with you always</li>
            <li>Track your symptoms and peak flow readings</li>
        </ul>
        """
    else:
        return """
        <h3>General Wellness Tips</h3>
        <p>Maintain your health with these daily habits:</p>
        <ul>
            <li>Get 7-9 hours of quality sleep each night</li>
            <li>Eat a balanced diet rich in fruits and vegetables</li>
            <li>Stay physically active - find activities you enjoy</li>
            <li>Stay connected with friends and family</li>
            <li>Schedule regular preventive care visits</li>
        </ul>
        """