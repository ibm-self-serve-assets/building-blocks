CREATE TABLE `factory-risk-signals` AS
SELECT
  `siteId`, `assetId`, `timestamp` AS `eventTime`,
  CASE WHEN `vibration` > 5.2 THEN 'BEARING_RISK'
       WHEN `temperature` > 72 THEN 'THERMAL_RISK'
       ELSE 'QUALITY_RISK' END AS `riskType`,
  CAST(CASE WHEN `vibration` > 5.2 THEN `vibration` * 11.0
            WHEN `temperature` > 72 THEN `temperature`
            ELSE (100.0 - `qualityScore`) * 4.0 END AS DOUBLE) AS `riskScore`,
  CASE WHEN `vibration` > 6.5 OR `temperature` > 85 OR `qualityScore` < 80
       THEN 'critical' ELSE 'warning' END AS `severity`,
  'Flink threshold breached; operator review required' AS `message`
FROM `factory-iot-telemetry`
WHERE `vibration` > 5.2 OR `temperature` > 72 OR `qualityScore` < 86
