# JSON Schemas registered as topic-key and topic-value subjects for Confluent governance.

_str = {"type": "string"}
_num = {"type": "number"}
_integer = {"type": "integer"}
_bool = {"type": "boolean"}


def object(properties, required=None):
    if required is None:
        required = list(properties.keys())
    return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": False, "properties": properties, "required": required}


VALUE_SCHEMAS = {
    "factory-iot-telemetry": object({
        "eventId": _str, "timestamp": _str, "siteId": _str, "siteName": _str, "assetId": _str,
        "assetType": _str, "lineId": _str, "scenario": _str, "temperature": _num, "vibration": _num,
        "rpm": _integer, "energyKw": _num, "qualityScore": _num, "health": _integer, "status": _str, "batchId": _str,
    }),
    "factory-maintenance-events": object({
        "eventId": _str, "timestamp": _str, "siteId": _str, "assetId": _str, "eventType": _str,
        "severity": _str, "message": _str, "acknowledged": _bool,
    }),
    "factory-asset-state": object({
        "assetId": _str, "siteId": _str, "timestamp": _str, "status": _str, "health": _integer,
        "temperature": _num, "vibration": _num, "qualityScore": _num, "scenario": _str,
    }),
}
KEY_SCHEMA = object({"id": _str})
