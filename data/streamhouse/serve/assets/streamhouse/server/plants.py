# Fictional factory sites at real US city coordinates, not representations of actual facilities.
#
# oee_base: realistic steady-state OEE % for this plant type.
#   Automotive body shops: ~92–94 % (high-volume, complex, well-maintained)
#   Battery module lines: ~88–90 % (newer, still ramping)
#   Precision CNC: ~85–87 % (tight tolerances, frequent changeover)
#   Electronics assembly: ~93–95 % (high-speed, mature process)
#   Industrial machinery: ~89–91 % (mixed manual / automated)
#   Packaging / fulfilment: ~95–97 % (simple, high-speed)
#
# rate: units produced per active line per minute at 100 % OEE.
#   Automotive subframes: ~8 u/min per line (cycle ~7 s)
#   Battery modules: ~5 u/min per line (complex, multi-step)
#   Precision CNC: ~12 u/min per line (small parts, fast spindle)
#   Electronics PCBs: ~40 u/min per line (surface-mount speed)
#   Industrial machines: ~4 u/min per line (large assemblies)
#   Packaging cases: ~60 u/min per line (case-packing rates)
PLANTS = [
    {"id": "DET", "name": "Detroit Assembly",      "city": "Detroit",   "state": "Michigan",       "lat": 42.3314, "lng":  -83.0458, "type": "Automotive assembly",    "lines": 8, "robots": 12, "region": "MIDWEST", "asset": "EV body shop",           "oee_base": 93.0, "rate":  8},
    {"id": "AUS", "name": "Austin Gigafactory",    "city": "Austin",    "state": "Texas",          "lat": 30.2672, "lng":  -97.7431, "type": "Battery / robotics",     "lines": 6, "robots": 14, "region": "SOUTH",   "asset": "Battery module line",    "oee_base": 89.0, "rate":  5},
    {"id": "SEA", "name": "Seattle Precision",     "city": "Seattle",   "state": "Washington",     "lat": 47.6062, "lng": -122.3321, "type": "Precision components",   "lines": 5, "robots": 10, "region": "WEST",    "asset": "CNC fabrication",        "oee_base": 86.0, "rate": 12},
    {"id": "PHX", "name": "Phoenix Semicon",       "city": "Phoenix",   "state": "Arizona",        "lat": 33.4484, "lng": -112.0740, "type": "Electronics",            "lines": 7, "robots": 16, "region": "WEST",    "asset": "Electronics assembly",   "oee_base": 94.0, "rate": 40},
    {"id": "CLT", "name": "Charlotte Manufacturing","city": "Charlotte", "state": "North Carolina", "lat": 35.2271, "lng":  -80.8431, "type": "Industrial machinery",   "lines": 6, "robots": 11, "region": "EAST",    "asset": "Machine tool assembly",  "oee_base": 90.0, "rate":  4},
    {"id": "CHI", "name": "Chicago Distribution",  "city": "Chicago",   "state": "Illinois",       "lat": 41.8781, "lng":  -87.6298, "type": "Packaging / fulfillment","lines": 4, "robots":  9, "region": "MIDWEST", "asset": "Smart packaging",        "oee_base": 96.0, "rate": 60},
]
ROBOT_TYPES = ["Welding robot", "Pick & place", "Quality scanner", "Assembly cobot", "AGV transporter", "Packaging arm"]
SCENARIOS = [
    {"id": "baseline", "name": "Healthy operations", "description": "All assets normal; deterministic live industrial telemetry."},
    {"id": "bearing", "name": "Bearing wear", "description": "Vibration increases before a predictive maintenance alarm."},
    {"id": "thermal", "name": "Thermal excursion", "description": "Heat and energy consumption spike on the production line."},
    {"id": "quality", "name": "Quality drift", "description": "Inspection rejects rise and yield drops across a batch."},
    {"id": "surge", "name": "Demand surge", "description": "Higher conveyor speed boosts output and load."},
]
