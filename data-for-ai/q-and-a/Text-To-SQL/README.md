# 🧠 watsonx.data Text-to-SQL Onboarding and Applications

This repository provides a detailed **onboarding and usage guide** for the **Text-to-SQL API service** that is part of **IBM watsonx.data Intelligence**.

This service allows users to convert **natural language queries** into **SQL statements** for supported databases — empowering business users and data scientists to interact with their data seamlessly without writing SQL.

---

## 📑 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Project Structure](#project-structure)
7. [Developer Guide](#developer-guide)
8. [Examples](#examples)
9. [Business Value](#business-value)
10. [Use Cases](#use-cases)
11. [Benefits](#benefits)
12. [Contributing](#contributing)
13. [License](#license)

---

## 🧠 Overview

The **Text-to-SQL service** in **watsonx.data Intelligence** enables users to translate natural language questions into SQL queries that can be executed on their data assets.

This guide walks through:
- Provisioning and onboarding the **watsonx.data Intelligence** service.
- Integrating **Text-to-SQL APIs**.
- Querying imported datasets using natural language.

### Key Objectives:
- Simplify data access for non-technical users.
- Reduce manual query creation.
- Enable faster insights through AI-powered query generation.

---

## 🏗️ Architecture

The Text-to-SQL service leverages the **watsonx.data Intelligence API layer** to generate SQL queries dynamically based on the schema metadata of your onboarded projects.

![Architecture Diagram](images/image.png)

### Workflow
1. **User Input (Natural Language Query):** “Show me total sales by region.”
2. **Text-to-SQL API:** Converts the query to SQL syntax using an LLM.
3. **watsonx.data Intelligence:** Executes the query against the connected data source.
4. **Response:** Returns structured query results.

### Supported SQL Dialects
- Presto
- PostgreSQL
- Microsoft SQL Server
- Oracle
- Snowflake

---

## ✨ Features

- **Natural Language Querying:** No SQL expertise required.
- **Automatic Query Generation:** Converts natural text into SQL syntax.
- **Schema Awareness:** Utilizes metadata from onboarded projects for contextual accuracy.
- **Multi-Model Support:** Integrates with LLMs like `meta-llama/llama-3-3-70b-instruct` and IBM’s `granite` models.
- **Multi-Dialect Compatibility:** Supports multiple database dialects (Presto, PostgreSQL, etc.)
- **Secure API Access:** IBM IAM-based token authentication for all API interactions.

---

## 🧰 Technology Stack

| Component | Description |
|------------|-------------|
| **IBM watsonx.data Intelligence** | Core platform for Text-to-SQL orchestration |
| **watsonx.ai Models** | LLMs used to interpret natural language |
| **IBM Cloud IAM** | Authentication and secure API access |
| **RESTful APIs** | Endpoints for onboarding and query execution |
| **Supported Databases** | Presto, PostgreSQL, Oracle, MSSQL, Snowflake |

---

## ⚙️ Prerequisites

1. **IBM Cloud Account**
2. **watsonx.data Intelligence instance**
   - [IBM Cloud Catalog – watsonx.data Intelligence](https://cloud.ibm.com/catalog#all_products)
3. **IBM Cloud API Key**
   - [Guide: Creating API Keys](https://cloud.ibm.com/docs/account?topic=account-userapikey&interface=ui#create_user_key)
4. **Data Assets**
   - Preloaded tables in PrestoDB or other supported data sources.

**Supported Dialects:** presto, postgresql, mssql, oracle, presto_sql, snowflake

---

## 📁 Project Structure

```
watsonxdata-text2sql/
│
├── images/                      # Architecture and workflow diagrams
├── config/                      # Example configurations and curl commands
├── examples/                    # Example queries and outputs
├── README.md                    # Documentation
└── scripts/                     # Optional helper scripts
```

---

## 👩‍💻 Developer Guide

Follow the steps below to set up and use the **Text-to-SQL API** within your IBM watsonx.data Intelligence project.

### Step 1: Provision watsonx.data Intelligence
1. Provision the service instance from the [IBM Cloud Catalog](https://cloud.ibm.com/catalog#all_products).
   - **Region:** Currently supported – Toronto (`ca-tor`)
2. Create a new **project** and note down your **Project ID**.
   - Navigate to **Manage → General → Project ID**

### Step 2: Onboard Your Project via API

1. **Generate an IBM IAM Bearer Token:**

```bash
curl -X POST 'https://iam.cloud.ibm.com/identity/token' -H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=<YOUR_IBM_CLOUD_API_KEY>'
```

2. **Onboard Project for Text-to-SQL Capabilities:**

```bash
curl --location --request PUT 'https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/onboard_for_text_2_sql' --header 'accept: application/json' --header 'Content-Type: application/json' --header 'Authorization: Bearer <YOUR_BEARER_TOKEN>' --data '{
  "containers": [
    {
      "container_id": "<YOUR_PROJECT_ID>",
      "container_type": "project"
    }
  ]
}'
```

### Step 3: Create a Data Connection and Import Data Assets

1. Navigate to your **watsonx.data Intelligence** project.
2. Follow this [guide](https://dataplatform.cloud.ibm.com/docs/content/wsj/manage-data/create-conn.html?context=wx&locale=en) to:
   - Add a data connection.
   - Import assets (tables) for querying.

### Step 4: Run a Text-to-SQL Query

```bash
curl --location 'https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/text_to_sql?container_id=<YOUR_PROJECT_ID>&container_type=project&dialect=<YOUR_DIALECT>&model_id=meta-llama%2Fllama-3-3-70b-instruct' --header 'accept: application/json' --header 'Content-Type: application/json' --header 'Authorization: Bearer <YOUR_BEARER_TOKEN>' --data '{
  "query": "<YOUR_QUERY>",
  "raw_output": true
}'
```

**Parameters:**
- `container_id`: Your Project ID  
- `dialect`: Corresponding SQL dialect (e.g., presto, postgres)  
- `model_id`: Optional – defaults to `ibm/granite-3-8b-instruct`  

### Step 5: Tune Query Responses
- Fine-tune prompts to get more specific SQL results.
- Ensure metadata is refreshed after adding or modifying tables.
- Re-onboard the project if schema changes significantly.

### Step 6: Troubleshooting

#### Common Error:
```
"message": "text2sql: No matches were found in metadata index for input query..."
```
✅ **Resolution:** Ensure your project is onboarded before importing assets.

---

## 🧩 Examples

| Input Query | Generated SQL |
|--------------|----------------|
| “Show me total revenue by product category” | `SELECT category, SUM(revenue) FROM sales GROUP BY category;` |
| “List top 5 customers by purchase value” | `SELECT customer_name, SUM(purchase_amount) FROM transactions GROUP BY customer_name ORDER BY 2 DESC LIMIT 5;` |

---

## 💼 Business Value

- **Empowers Non-Technical Users:** Query data without SQL knowledge.
- **Reduces Developer Load:** Less dependency on data engineers for ad-hoc reporting.
- **Accelerates Insights:** Natural language to SQL saves hours of manual query building.
- **Integrates Seamlessly:** Works within IBM’s watsonx ecosystem.

---

## 🌍 Use Cases

- **Data Exploration:** Quickly extract insights without writing SQL.
- **Business Intelligence:** Enable self-service reporting for business teams.
- **Customer Analytics:** Query sales or customer data dynamically.
- **Governed AI Integrations:** Combine with watsonx.ai models for intelligent data workflows.

---

## 🚀 Benefits

| Category | Description |
|-----------|-------------|
| **Efficiency** | Automates query writing for faster results |
| **Accessibility** | Empowers non-technical users |
| **Governance** | Built within IBM watsonx security framework |
| **Scalability** | Works across multiple databases and regions |
| **Flexibility** | Compatible with multiple SQL dialects |

---

## 🤝 Contributing

Contributions are welcome!  
If you’d like to enhance the Text-to-SQL Building Block:
1. Fork this repository  
2. Create a feature branch (`feature/improve-docs`)  
3. Submit a Pull Request  

---

## ⚖️ License

This project is licensed under the **Apache 2.0 License**.  
See the [LICENSE](./LICENSE) file for details.

---

**Next Steps:**
- Explore [watsonx.data Intelligence Documentation](https://www.ibm.com/docs/en/watsonx/wdi)  
- Try integrating this service with **watsonx.ai** or **watsonx Orchestrate** for intelligent query automation  
- Use this as a foundation for custom analytics agent development  
