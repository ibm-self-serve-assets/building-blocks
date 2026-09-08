# Context

Context building blocks help developers combine **live events, governed metadata, data quality, lineage, and operational health** so applications and AI systems can consume trustworthy enterprise context.

## Building blocks

| Building block | IBM product anchor | Developer use |
|---|---|---|
| [Context Hub](context-hub/) | IBM Confluent + IBM watsonx.data + IBM watsonx.data intelligence | Compose live and governed context across streaming and data-at-rest |
| [Real-Time Streaming](real-time-streaming/) | IBM Confluent | Build Kafka/Flink event-streaming solutions and streaming demos |
| [Metadata Enrichment & Data Quality](metadata-enrichment/) | IBM watsonx.data intelligence | Add business context, quality rules, and lineage |
| [Data Observability](data-observability/) | IBM watsonx.data integration — Data Observability | Monitor pipeline/run health, anomalies, SLAs, and alerts |

## How the capabilities fit

```text
Enterprise systems / events
          |
          v
    IBM Confluent
 streaming + processing
          |
          +--------------------+
          |                    |
          v                    v
 IBM watsonx.data       Operational pipelines
 data-at-rest / SQL             |
          |                     v
          |        watsonx.data integration
          |          Data Observability
          |
          v
IBM watsonx.data intelligence
metadata + quality + lineage
          |
          v
Applications / analytics / AI
```

Start with the smallest building block that solves the requirement. Use **Context Hub** only when you intentionally need to compose several of these capabilities.

## IBM references

- IBM Confluent: https://www.ibm.com/products/confluent
- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
