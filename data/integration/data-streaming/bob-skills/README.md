# Data Streaming Bob Skills

This directory contains Bob skills for data streaming operations using Confluent Kafka.

## Available Skill

The `data-streaming-confluent.zip` file contains the following skill:

### data-streaming-confluent
A comprehensive skill for working with Confluent Kafka, providing capabilities for:
- Creating Confluent backbone infrastructure
- Producing messages to Kafka topics
- Consuming messages from Kafka topics
- Interacting with Confluent Schema Registry
- Managing Kafka streaming operations

## Installation and Setup

### Step 1: Download the Skill
Download the `data-streaming-confluent.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents of `data-streaming-confluent.zip` to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/data-streaming-confluent.zip
```

After extraction, you should see a `data-streaming-confluent` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/data-streaming-confluent
```

You should see the skill files and configuration.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `data-streaming-confluent` skill will be available for use within that mode

## Usage

Once activated, the **data-streaming-confluent** skill provides comprehensive functionality for working with Confluent Kafka:

- **Confluent Backbone Creation**: Set up and configure Confluent infrastructure backbone
- **Message Production**: Send messages to Kafka topics
- **Message Consumption**: Read and process messages from Kafka topics
- **Schema Management**: Work with Confluent Schema Registry for Avro, JSON, and Protobuf schemas
- **Stream Processing**: Handle real-time data streaming operations

## Requirements

Before using this skill, ensure you have:
- Access to a Confluent Kafka cluster
- Valid credentials and appropriate permissions
- Schema Registry access (if using schema features)
- Network connectivity to your Kafka cluster

## Configuration

After installation, you may need to configure the skill with your Kafka cluster details:
- Kafka broker endpoints
- Authentication credentials
- Schema Registry URL (if applicable)
- Topic names and configurations

Refer to the skill's internal documentation for specific configuration parameters.

## Troubleshooting

If the skill doesn't appear after installation:
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

## Support

For issues or questions about this skill, please refer to the main documentation or contact your administrator.