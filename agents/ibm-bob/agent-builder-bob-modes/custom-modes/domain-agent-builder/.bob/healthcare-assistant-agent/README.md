# Healthcare Assistant Agent

**"Your Health, Our Priority"**

A comprehensive watsonx Orchestrate agent for healthcare management, patient care coordination, and personalized healthcare communications.

## Overview

The Healthcare Assistant Agent helps healthcare providers manage patient care across different care levels (Outpatient, Inpatient, ICU, Emergency) with capabilities for:

- **Appointment Management**: Schedule and manage appointments across all care levels
- **Medical Records Access**: Securely retrieve patient profiles and medical history
- **Prescription Management**: Process prescription refill requests
- **Care Reminders**: Send personalized care reminders and wellness tips
- **Insurance & Billing**: Handle insurance inquiries and billing questions

## Quick Start

### Prerequisites

- watsonx Orchestrate account with API access
- Python 3.8+ environment
- watsonx Orchestrate CLI (`orchestrate`) installed
- WXO_API_KEY environment variable set

### Deployment

1. **Set your API key**:
   ```bash
   export WXO_API_KEY='your-api-key-here'
   ```

2. **Navigate to the project directory**:
   ```bash
   cd bob/healthcare-assistant-agent
   ```

3. **Make deployment scripts executable**:
   ```bash
   chmod +x scripts/*.sh
   ```

4. **Deploy the complete agent**:
   ```bash
   ./scripts/deploy_all.sh
   ```

The deployment script will:
- Import patient management tools
- Import communication generation tools
- Import the healthcare patient knowledge base
- Deploy the Healthcare Assistant Agent

## Project Structure

```
healthcare-assistant-agent/
├── agent_config.yaml              # Main agent configuration
├── .env                           # Environment variables (API key)
├── .env.example                   # Example environment file
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── TROUBLESHOOTING.md            # Troubleshooting guide
├── tools/
│   ├── patient_tools.py          # Patient management functions
│   └── communication_tools.py    # Communication generation
├── data/
│   └── patients.csv              # Sample patient data
├── knowledge_bases/
│   └── healthcare_patient_kb.yaml # Knowledge base configuration
├── scripts/
│   ├── deploy_all.sh             # Complete deployment
│   ├── import_tools.sh           # Import tools only
│   ├── import_kb.sh              # Import knowledge base only
│   └── deploy_agent.sh           # Deploy agent only
└── docs/
    └── architecture.md           # Architecture documentation
```

## Care Levels

The agent supports four care levels with different priorities:

### 1. **Outpatient** (Normal Priority)
- Routine care and scheduled visits
- Preventive services
- Follow-up appointments
- Wellness programs

### 2. **Inpatient** (Medium Priority)
- Hospital admission
- Ongoing treatment
- Recovery monitoring
- Discharge planning

### 3. **ICU** (High Priority)
- Intensive care
- Critical monitoring
- Specialized treatment
- Family communication

### 4. **Emergency** (Urgent Priority)
- Urgent care
- Immediate attention
- Rapid assessment
- Emergency protocols

## Available Tools

### Patient Management Tools

#### `get_patient_data`
Retrieve patient data with flexible filtering options.

**Parameters:**
- `patient_id` (optional): Filter by specific patient ID
- `care_level` (optional): Filter by care level
- `status` (optional): Filter by status (active, critical, urgent)
- `limit` (optional): Maximum number of results

**Example:**
```python
get_patient_data(care_level="ICU", status="critical")
```

#### `get_patient_by_id`
Get a specific patient by their unique identifier.

**Parameters:**
- `patient_id` (required): The patient's unique ID

**Example:**
```python
get_patient_by_id("PAT001")
```

#### `get_patients_by_care_level`
Retrieve all patients in a specific care level.

**Parameters:**
- `care_level` (required): The care level (Outpatient, Inpatient, ICU, Emergency)

**Example:**
```python
get_patients_by_care_level("ICU")
```

#### `calculate_patient_metrics`
Calculate aggregated metrics for patients.

**Parameters:**
- `care_level` (optional): Filter by care level

**Example:**
```python
calculate_patient_metrics()
```

### Communication Tools

#### `generate_patient_communication`
Generate personalized healthcare communications.

**Parameters:**
- `patient_id` (required): The patient's unique ID
- `communication_type` (required): Type of communication
  - `appointment_confirmation`
  - `lab_result_alert`
  - `medication_reminder`
  - `wellness_tip`
  - `billing_notice`
- `additional_context` (optional): Additional information to include

**Example:**
```python
generate_patient_communication(
    patient_id="PAT001",
    communication_type="appointment_confirmation"
)
```

## Sample Queries

Try these queries with the Healthcare Assistant Agent:

### Patient Information
- "Show me all ICU patients"
- "Get patient data for PAT001"
- "What patients are in critical condition?"
- "List all outpatient appointments this week"
- "Show me patients with diabetes"

### Care Coordination
- "Which patients need follow-up appointments?"
- "Show emergency patients from today"
- "List all inpatients in room 302"
- "What medications is PAT003 taking?"

### Communications
- "Generate an appointment confirmation for PAT005"
- "Send a medication reminder to PAT001"
- "Create a wellness tip for PAT007"
- "Generate a lab result alert for PAT002"
- "Send a billing notice to PAT004"

### Analytics
- "Calculate patient metrics for ICU"
- "How many patients are in each care level?"
- "Show me patient statistics"

## Customization

### Adding New Patients

Edit `data/patients.csv` to add new patient records:

```csv
patient_id,name,email,phone,date_of_birth,care_level,status,primary_physician,...
PAT011,New Patient,email@example.com,555-0121,1980-01-01,Outpatient,active,Dr. Smith,...
```

After updating, reimport the knowledge base:
```bash
./scripts/import_kb.sh
```

### Adding New Tools

1. Create a new Python file in `tools/` directory
2. Use the `@tool` decorator from `ibm_watsonx_orchestrate.agent_builder.tools`
3. Add proper type hints and docstrings
4. Import the tool:
   ```bash
   orchestrate tools import -k python -f tools/your_new_tool.py
   ```
5. Update `agent_config.yaml` to reference the new tool

### Modifying Communication Templates

Edit `tools/communication_tools.py` to customize:
- Email templates and styling
- Care level-specific messaging
- Wellness content based on conditions
- Priority and urgency indicators

### Updating Agent Configuration

Modify `agent_config.yaml` to change:
- Agent instructions and behavior
- Tool references
- Knowledge base connections
- LLM model selection

After changes, redeploy:
```bash
./scripts/deploy_agent.sh
```

## Data Privacy & Security

⚠️ **IMPORTANT**: This agent handles sensitive healthcare information.

- **HIPAA Compliance**: Ensure all deployments comply with HIPAA regulations
- **Data Security**: Never commit real patient data to version control
- **Access Control**: Implement proper authentication and authorization
- **Audit Logging**: Enable logging for all patient data access
- **Encryption**: Use encryption for data at rest and in transit

### Best Practices

1. Replace sample data with anonymized or synthetic data for testing
2. Use environment variables for all sensitive configuration
3. Implement role-based access control (RBAC)
4. Regular security audits and compliance reviews
5. Data retention policies aligned with regulations

## Testing

### Manual Testing

1. Access watsonx Orchestrate interface
2. Select the Healthcare Assistant Agent
3. Try sample queries from the "Sample Queries" section
4. Verify tool execution and responses

### Automated Testing

Run the test suite (if available):
```bash
cd tests
python -m pytest
```

## Troubleshooting

### Common Issues

**Issue**: Tools not found after deployment
**Solution**: Verify tools were imported successfully:
```bash
orchestrate tools list | grep -E "get_patient|generate_patient"
```

**Issue**: Knowledge base search not working
**Solution**: Reimport the knowledge base:
```bash
./scripts/import_kb.sh
```

**Issue**: Agent not responding
**Solution**: Check agent deployment status:
```bash
orchestrate agents list | grep healthcare_assistant
```

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Architecture

The Healthcare Assistant Agent follows a modular architecture:

- **Agent Layer**: Orchestrates tools and manages conversations
- **Tool Layer**: Implements specific healthcare functions
- **Data Layer**: Patient data and knowledge bases
- **Communication Layer**: Generates personalized messages

The agent follows a modular design with separate tool, data, and communication layers.

## Contributing

To contribute to this agent:

1. Follow the existing code structure and patterns
2. Add comprehensive docstrings to all functions
3. Include type hints for all parameters
4. Test thoroughly before deployment
5. Update documentation for any changes

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review watsonx Orchestrate documentation
- Contact your watsonx Orchestrate administrator

## License

This agent is provided as-is for use with IBM watsonx Orchestrate.

## Version History

- **v1.0** (2026-02-04): Initial release
  - Patient management tools
  - Communication generation
  - Four care levels support
  - Sample patient data
  - Complete deployment automation

---

**Healthcare Assistant Agent** - Built with IBM watsonx Orchestrate