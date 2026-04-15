# Data Security & Encryption Capability

## Building Blocks

### Data Protection Automation
**Location**: `data-protection-automation/`  
**IBM Products**: IBM Cloud, watsonx.data, IBM Key Protect  
**Description**: Automated data protection and security configuration

**Quick Start**:
```bash
cd data-protection-automation
export IBM_CLOUD_API_KEY="your-api-key"
export WATSONX_DATA_INSTANCE_ID="your-instance-id"
pip install ibm-cloud-sdk-core ibm-watsonx-data
python setup_ibm_projects_catalog.py
```

**What it does**:
- Creates IBM Cloud project
- Sets up data catalog
- Configures protection rules
- Enables encryption
- Sets up access controls
- Configures audit logging

---

For detailed setup, see component README.