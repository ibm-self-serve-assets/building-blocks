-- Automated analogue of a Topic Action transformation, NOT a console-created Action.
-- A curated downstream copy that masks the production batch identifier.
CREATE TABLE `factory-governed-telemetry` AS
SELECT
  `eventId`, `timestamp`, `siteId`, `assetId`,
  `temperature`, `vibration`, `rpm`, `energyKw`, `qualityScore`,
  'MASKED' AS `batchId`, `scenario`
FROM `factory-iot-telemetry`
