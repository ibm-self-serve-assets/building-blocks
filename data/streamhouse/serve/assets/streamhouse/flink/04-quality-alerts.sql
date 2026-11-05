-- Streamhouse TRANSFORM: prepare quality decisions for downstream systems.
INSERT INTO `factory-quality-alerts`
SELECT
  `siteId`, `assetId`, `batchId`, `qualityScore`, `timestamp` AS `eventTime`,
  CASE WHEN `qualityScore` < 78 THEN 'QUARANTINE_BATCH'
       ELSE 'REQUEST_INSPECTION' END AS `action`
FROM `factory-iot-telemetry`
WHERE `qualityScore` < 86;
