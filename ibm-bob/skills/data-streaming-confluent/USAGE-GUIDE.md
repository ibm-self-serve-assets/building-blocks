# Data Streaming Confluent Skill - Usage Guide

This guide explains how to use the Data Streaming Confluent skill to create production-ready streaming solutions on Confluent Cloud.

## Table of Contents

1. [Quick Start](#quick-start)
2. [How to Describe Your Use Case](#how-to-describe-your-use-case)
3. [Understanding Generated Solutions](#understanding-generated-solutions)
4. [Deployment Workflow](#deployment-workflow)
5. [Testing and Validation](#testing-and-validation)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Quick Start

### Step 1: Describe Your Business Problem

Simply tell the skill what you're trying to solve. Be specific about:
- **Domain**: What industry or business area?
- **Entities**: What are the key things you're tracking?
- **Events**: What happens that you need to process?
- **Goals**: What insights or actions do you need?

**Example:**
```
"Build a fraud detection system for credit card transactions. 
We process 10,000 transactions per minute and need to detect:
- High transaction velocity (>10 in 5 minutes)
- Unusual amounts (>$5000)
- Suspicious locations
Calculate risk scores and alert on high-risk transactions."
```

### Step 2: Review Generated Solution

The skill will generate a complete solution with:
- Terraform infrastructure files
- Flink SQL processing logic
- Python producers with sample data
- Comprehensive documentation
- Automation scripts

### Step 3: Deploy

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup.sh
```

### Step 4: Test

```bash
# Produce test data
./scripts/test.sh

# Validate with Flink SQL queries (see docs/TESTING.md)
```

### Step 5: Cleanup

```bash
# Remove all resources
./scripts/cleanup.sh
```

---

## How to Describe Your Use Case

### Template for Effective Requests

```
"Build a [type of system] for [domain/industry].

Requirements:
- [Key requirement 1]
- [Key requirement 2]
- [Key requirement 3]

Scale:
- [Volume information]
- [Velocity information]

Business Rules:
- [Specific logic or constraints]"
```

### Examples by Domain

#### Financial Services
```
"Create a real-time payment processing system that:
- Validates transactions against account balances
- Detects duplicate transactions within 1 minute
- Calculates daily transaction totals per account
- Alerts on suspicious patterns
- Processes 50,000 transactions per hour"
```

#### IoT / Manufacturing
```
"Build a machine monitoring system that:
- Collects sensor data from 200 machines every 10 seconds
- Calculates 5-minute rolling averages for temperature and vibration
- Detects anomalies (values outside normal ranges)
- Tracks machine uptime and downtime
- Generates maintenance alerts"
```

#### E-commerce / Retail
```
"Develop an inventory management system that:
- Tracks stock levels across 50 stores in real-time
- Processes sales and restocking events
- Calculates available inventory per SKU per location
- Alerts on low stock (< 10 units)
- Handles 5,000 inventory updates per minute"
```

#### Healthcare
```
"Create a patient monitoring system that:
- Collects vital signs from 100 patients every 30 seconds
- Calculates 10-minute averages for heart rate and blood pressure
- Detects critical thresholds (heart rate >120 or <50)
- Tracks patient status changes
- Generates immediate alerts for critical conditions"
```

### What to Include

✅ **DO Include:**
- Business domain and context
- Key entities (customers, devices, products, etc.)
- Event types (transactions, readings, updates, etc.)
- Processing requirements (aggregations, filtering, joins)
- Scale information (volume, velocity)
- Specific thresholds or business rules
- Alert conditions

❌ **DON'T Include:**
- Specific Kafka topic names (skill will generate appropriate names)
- Technical implementation details (skill handles this)
- Infrastructure sizing (skill uses appropriate defaults)
- Schema definitions (skill designs based on requirements)

---

## Understanding Generated Solutions

### Directory Structure

Every generated solution follows this structure:

```
your-solution/
├── terraform/              # Infrastructure as Code
│   ├── providers.tf       # Confluent provider config
│   ├── variables.tf       # Configurable parameters
│   ├── main.tf           # Core resources
│   ├── outputs.tf        # Credentials and endpoints
│   └── terraform.tfvars.example
│
├── python/                # Data producers
│   ├── producers/
│   │   └── produce_messages.py
│   ├── requirements.txt
│   ├── .env.example
│   └── sample-data/
│
├── flink/                 # Stream processing (optional)
│   ├── tables/           # Table definitions
│   ├── jobs/             # Processing jobs
│   └── queries/          # Test queries
│
├── scripts/               # Automation
│   ├── setup.sh          # One-command deployment
│   ├── test.sh           # Validation testing
│   └── cleanup.sh        # Resource cleanup
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md   # Solution design
│   ├── SETUP.md          # Deployment guide
│   ├── TESTING.md        # Validation procedures
│   └── TROUBLESHOOTING.md
│
└── README.md              # Quick start
```

### Key Components

#### 1. Terraform Infrastructure (`terraform/`)

**What it creates:**
- Confluent Cloud environment
- Kafka cluster (Basic tier)
- Domain-specific topics
- Schema Registry (auto-provisioned)
- Flink compute pool
- Service accounts with proper RBAC
- API keys for Kafka, Flink, and Schema Registry

**Key files:**
- `main.tf` - All resource definitions
- `variables.tf` - Configurable parameters
- `outputs.tf` - Credentials and connection info
- `terraform.tfvars` - Your specific values (created from .example)

#### 2. Flink SQL Processing (`terraform/main.tf`)

**What it includes:**
- Source table definitions (input topics)
- Destination table definitions (output topics)
- Processing jobs (aggregations, filtering, joins)
- Proper schema registration

**Key patterns:**
- Windowed aggregations (TUMBLE, HOP)
- Stateful processing (GROUP BY)
- Stream joins
- Filtering and transformations

#### 3. Python Producers (`python/`)

**What it provides:**
- Schema-aware message production
- Sample data generation
- Error handling and monitoring
- Delivery callbacks

**Key features:**
- Retrieves schemas from Schema Registry
- Uses JSON Schema serialization
- Proper key/value formatting
- Timestamp handling (milliseconds)

#### 4. Documentation (`docs/`)

**What it contains:**
- Architecture diagrams (Mermaid)
- Step-by-step setup instructions
- Testing procedures with SQL queries
- Troubleshooting guides
- Cleanup procedures

#### 5. Automation Scripts (`scripts/`)

**What they do:**
- `setup.sh` - Complete deployment automation
- `test.sh` - Produce test data
- `cleanup.sh` - Safe resource removal

---

## Deployment Workflow

### Prerequisites

Before deploying, ensure you have:

1. **Confluent Cloud Account**
   - Sign up at https://confluent.cloud
   - Create Cloud API key and secret
   - Note your organization ID

2. **Local Tools**
   - Terraform >= 1.0
   - Python >= 3.8
   - pip3
   - bash shell

3. **Credentials**
   - Confluent Cloud API key
   - Confluent Cloud API secret

### Deployment Steps

#### Option 1: Automated Deployment (Recommended)

```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Run setup script
./scripts/setup.sh

# The script will:
# - Check prerequisites
# - Create terraform.tfvars from example
# - Prompt for credentials
# - Deploy infrastructure
# - Setup Python environment
# - Verify configuration
```

#### Option 2: Manual Deployment

```bash
# 1. Configure Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your credentials

# 2. Deploy infrastructure
terraform init
terraform validate
terraform plan
terraform apply

# 3. Setup Python
cd ../python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Verify .env file was created
cat .env
```

### Post-Deployment Verification

After deployment, verify:

1. **Confluent Cloud Console**
   - Environment created
   - Cluster running
   - Topics created
   - Flink compute pool active

2. **Local Configuration**
   - `.env` file exists in `python/`
   - Contains all required variables
   - No placeholder values

3. **RBAC Permissions**
   - Wait 30 seconds after deployment
   - Permissions need time to propagate

---

## Testing and Validation

### Producing Test Data

```bash
# Using automation script
./scripts/test.sh

# Or manually
cd python
source venv/bin/activate
python producers/produce_messages.py
```

### Validating Results

#### 1. Check Raw Stream

```sql
-- View recent messages
SELECT * FROM source_table 
ORDER BY timestamp_column DESC 
LIMIT 10;
```

**What to verify:**
- ✅ Messages are flowing
- ✅ Schema is correct
- ✅ Timestamps are recent
- ✅ Data looks realistic

#### 2. Check Aggregated Results

```sql
-- View processed results
SELECT * FROM destination_table 
ORDER BY key_column 
LIMIT 20;
```

**What to verify:**
- ✅ Aggregations are correct
- ✅ Keys are properly set
- ✅ Values match expectations
- ✅ No duplicate keys (for upsert tables)

#### 3. Check Windowed Aggregations

```sql
-- View time-based windows
SELECT 
  window_start,
  window_end,
  key_column,
  aggregated_value
FROM windowed_table
ORDER BY window_start DESC
LIMIT 20;
```

**What to verify:**
- ✅ Windows are correct size
- ✅ Aggregations within windows are correct
- ✅ No missing windows
- ✅ Watermarks advancing properly

#### 4. Check Business Logic

```sql
-- Verify specific business rules
SELECT * FROM alerts_table
WHERE severity = 'HIGH'
ORDER BY alert_time DESC;
```

**What to verify:**
- ✅ Alerts triggered correctly
- ✅ Thresholds working
- ✅ Business rules applied
- ✅ No false positives/negatives

### Common Issues and Solutions

#### No Data in Destination Table

**Possible causes:**
1. RBAC permissions not propagated (wait 30s)
2. Flink job not running (check Console)
3. Consumer isolation level not set
4. Schema mismatch

**Solutions:**
```sql
-- Check if source has data
SELECT COUNT(*) FROM source_table;

-- Check Flink job status in Console
-- Wait 30 seconds after deployment
-- Verify consumer isolation level in table definition
```

#### Windowed Aggregations Not Triggering

**Possible causes:**
1. Watermark not advancing
2. Events not aligned to window boundaries
3. Not enough events to close window

**Solutions:**
- Produce events after window end time
- Align test data to window boundaries
- Check watermark configuration

---

## Customization

### Modifying Topic Configuration

Edit `terraform/main.tf`:

```hcl
# Change partition count
resource "confluent_kafka_topic" "my_topic" {
  # ...
  partitions_count = 6  # Change from default 4
}

# Add retention policy
resource "confluent_kafka_topic" "my_topic" {
  # ...
  config = {
    "retention.ms" = "604800000"  # 7 days
  }
}
```

### Adding New Flink Jobs

Add to `terraform/main.tf`:

```hcl
resource "confluent_flink_statement" "my_new_job" {
  # Copy structure from existing jobs
  statement = <<-SQL
    INSERT INTO destination
    SELECT ...
    FROM source
    WHERE ...
  SQL
  
  # Same properties, credentials, depends_on as other jobs
}
```

### Modifying Sample Data

Edit `python/sample-data/*.json`:

```json
[
  {
    "key_field": "new_value",
    "other_field": "updated_value",
    "timestamp": 1704067200000
  }
]
```

### Adding New Producers

Create `python/producers/my_producer.py`:

```python
# Copy structure from existing producer
# Modify schema retrieval
# Adjust message generation logic
```

---

## Troubleshooting

### Terraform Issues

#### Error: Invalid API credentials
```
Solution: Verify api_key and api_secret in terraform.tfvars
```

#### Error: Resource already exists
```
Solution: 
1. Check if resources exist in Console
2. Import existing resources or delete them
3. Run terraform apply again
```

#### Error: RBAC permissions denied
```
Solution:
1. Wait 30 seconds after role binding creation
2. Verify service account has correct roles
3. Check time_sleep resource is in depends_on
```

### Flink SQL Issues

#### Error: Table not found
```
Solution:
1. Verify table creation statement succeeded
2. Check sql.current-catalog and sql.current-database
3. Ensure proper depends_on chain
```

#### Error: Schema mismatch
```
Solution:
1. Check Schema Registry for registered schemas
2. Verify key and value formats match
3. Ensure producer uses same schema
```

### Python Producer Issues

#### Error: Schema not found
```
Solution:
1. Verify Flink tables created (they register schemas)
2. Check Schema Registry credentials in .env
3. Ensure schema name matches topic name
```

#### Error: Authentication failed
```
Solution:
1. Verify KAFKA_API_KEY and KAFKA_API_SECRET in .env
2. Check bootstrap servers format (no SASL_SSL:// prefix)
3. Ensure API key has CloudClusterAdmin role
```

---

## Best Practices

### Development Workflow

1. **Start Small**
   - Deploy with minimal configuration
   - Test with small data volumes
   - Validate before scaling

2. **Iterate Incrementally**
   - Add one feature at a time
   - Test after each change
   - Keep working versions

3. **Use Version Control**
   - Commit working configurations
   - Tag stable versions
   - Document changes

### Production Considerations

1. **Security**
   - Never commit credentials
   - Use separate environments (dev/prod)
   - Rotate API keys regularly
   - Use least-privilege RBAC

2. **Monitoring**
   - Set up alerts in Confluent Cloud
   - Monitor Flink job health
   - Track consumer lag
   - Watch for errors

3. **Cost Management**
   - Use Basic tier for development
   - Clean up unused resources
   - Monitor usage in Console
   - Set budget alerts

4. **Data Quality**
   - Validate schemas strictly
   - Handle errors gracefully
   - Log important events
   - Test edge cases

### Skill Usage Tips

1. **Be Specific**
   - Provide clear requirements
   - Include scale information
   - Specify business rules
   - Mention constraints

2. **Review Generated Code**
   - Understand the architecture
   - Verify business logic
   - Check configurations
   - Test thoroughly

3. **Customize Appropriately**
   - Start with generated code
   - Make targeted changes
   - Test after modifications
   - Document customizations

4. **Learn from Examples**
   - Study provided examples
   - Understand patterns
   - Adapt to your needs
   - Share learnings

---

## Next Steps

### After Successful Deployment

1. **Explore Confluent Cloud Console**
   - View topics and messages
   - Monitor Flink jobs
   - Check Schema Registry
   - Review metrics

2. **Experiment with Queries**
   - Try different aggregations
   - Test filtering logic
   - Explore windowing
   - Join multiple streams

3. **Extend the Solution**
   - Add new topics
   - Create additional jobs
   - Integrate with applications
   - Build dashboards

4. **Plan for Production**
   - Review security settings
   - Set up monitoring
   - Configure alerts
   - Document operations

### Learning Resources

- **Confluent Documentation**: https://docs.confluent.io
- **Flink SQL Reference**: https://docs.confluent.io/cloud/current/flink/reference/overview.html
- **Terraform Provider**: https://registry.terraform.io/providers/confluentinc/confluent/latest/docs
- **Examples**: See `examples/` directory in this skill

---

## Support

### Getting Help

1. **Check Documentation**
   - Review `docs/TROUBLESHOOTING.md`
   - Read Confluent Cloud docs
   - Search community forums

2. **Review Examples**
   - `examples/FRAUD-DETECTION-EXAMPLE.md`
   - `examples/IOT-MONITORING-EXAMPLE.md`

3. **Ask the Skill**
   - Describe your issue
   - Request specific modifications
   - Ask for explanations

### Common Questions

**Q: Can I use this for production?**
A: Yes, but review security settings, add monitoring, and test thoroughly.

**Q: How much does this cost?**
A: Depends on usage. Basic cluster + Flink compute pool. Monitor in Console.

**Q: Can I modify the generated code?**
A: Yes! Generated code is a starting point. Customize as needed.

**Q: What if I need help?**
A: Check docs, review examples, or ask the skill for specific guidance.

---

## Summary

This skill helps you:
- ✅ Transform business problems into streaming solutions
- ✅ Generate production-ready infrastructure code
- ✅ Create properly configured Confluent Cloud resources
- ✅ Implement stream processing with Flink SQL
- ✅ Build schema-aware data producers
- ✅ Deploy with automation scripts
- ✅ Test and validate solutions
- ✅ Clean up resources safely

**Remember:** Start simple, test thoroughly, iterate incrementally, and always clean up when done!