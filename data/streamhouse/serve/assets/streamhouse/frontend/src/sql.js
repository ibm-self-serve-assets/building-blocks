import create from '../flink/01-create-tables.sql?raw';
import risk from '../flink/02-risk-signal.sql?raw';
import kpis from '../flink/03-shift-kpis.sql?raw';
import quality from '../flink/04-quality-alerts.sql?raw';
export const SCRIPTS=[{id:'create',title:'01 · Schema & sources',description:'Register the governed Kafka-backed tables and value contracts.',code:create},{id:'risk',title:'02 · Predictive risk',description:'Continually detect elevated vibration, heat or declining quality.',code:risk},{id:'kpis',title:'03 · Shift performance',description:'Compute live 1-minute performance windows and factory utilization.',code:kpis},{id:'quality',title:'04 · Quality actions',description:'Route nonconforming batches into an actionable quality stream.',code:quality}];
