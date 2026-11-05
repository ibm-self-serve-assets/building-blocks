-- Factory Pulse / Confluent Cloud Flink SQL (run in the matching environment & Kafka cluster).
-- 1. First run the Node producer with STREAM_MODE=kafka. It registers JSON schemas
--    for factory-iot-telemetry, factory-asset-state and factory-maintenance-events.
-- 2. Confluent Flink can INFER input tables for Kafka topics with registered schemas.
--    Do NOT recreate these source tables: schemas and topics already exist.
SHOW TABLES;
DESCRIBE `factory-iot-telemetry`;
DESCRIBE `factory-asset-state`;
DESCRIBE `factory-maintenance-events`;

-- Create dedicated derived streams. Execute EACH statement separately.
CREATE TABLE `factory-risk-signals` (
  `siteId` STRING,
  `assetId` STRING,
  `eventTime` STRING,
  `riskType` STRING,
  `riskScore` DOUBLE,
  `severity` STRING,
  `message` STRING
);

CREATE TABLE `factory-shift-kpis` (
  `siteId` STRING,
  `windowStart` STRING,
  `sampleCount` BIGINT,
  `meanTemperature` DOUBLE,
  `meanVibration` DOUBLE,
  `meanQuality` DOUBLE,
  `energyKwhEstimate` DOUBLE
);

CREATE TABLE `factory-quality-alerts` (
  `siteId` STRING,
  `assetId` STRING,
  `batchId` STRING,
  `qualityScore` DOUBLE,
  `eventTime` STRING,
  `action` STRING
);
