-- Streamhouse TRANSFORM: rolling factory metrics over 1-minute tumbling windows.
-- Confluent Cloud Flink supports the system `$rowtime` attribute on inferred streams.
INSERT INTO `factory-shift-kpis`
SELECT
  `siteId`,
  CAST(window_start AS STRING) AS `windowStart`,
  COUNT(*) AS `sampleCount`,
  CAST(AVG(`temperature`) AS DOUBLE) AS `meanTemperature`,
  CAST(AVG(`vibration`) AS DOUBLE) AS `meanVibration`,
  CAST(AVG(`qualityScore`) AS DOUBLE) AS `meanQuality`,
  CAST(SUM(`energyKw`) / 60.0 AS DOUBLE) AS `energyKwhEstimate`
FROM TABLE(
  TUMBLE(TABLE `factory-iot-telemetry`, DESCRIPTOR($rowtime), INTERVAL '1' MINUTE)
)
GROUP BY `siteId`,window_start,window_end;
