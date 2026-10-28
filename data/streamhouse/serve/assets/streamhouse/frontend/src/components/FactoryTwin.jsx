import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import { createPlant } from '../twin/plantSim.js';
import { profileForSite } from '../twin/plantProfiles.js';
import { createLineController, ISSUE_TEXT } from '../twin/lineControl.js';

function PlantScene({ profile, control, onStatus, tags }) {
  const plant = useMemo(() => createPlant(profile), [profile]);
  useEffect(() => () => plant.dispose(), [plant]);
  const last = useRef('');

  useFrame((_, delta) => {
    const c = control.current;
    plant.update(c.playing ? Math.min(delta, 0.05) : 0, c);
    const s = plant.status();
    const key = `${s.state}|${s.faulted}|${s.warnings}|${s.units}|${s.rejects}|${s.cycle.toFixed(1)}|${s.rate.toFixed(2)}`;
    if (key !== last.current) { last.current = key; onStatus(s); }
  });

  const T = profile.theme;
  return <>
    <color attach="background" args={[T.bg]} />
    <fogExp2 attach="fog" args={[T.bg, 0.022]} />
    <primitive object={plant.group} />
    {plant.robots.map((r, i) => {
      const tag = tags[i];
      return <Html key={`${profile.id}-${i}`} position={r.label} center zIndexRange={[20, 0]} style={{ pointerEvents: 'none' }}>
        <div className={`robot-tag ${tag.tone}`}>
          <div><b>{tag.id}</b><span>{r.task}</span></div>
          {tag.headline && <em>{tag.headline}</em>}
          {tag.detail && <small>{tag.detail}</small>}
        </div>
      </Html>;
    })}
    <OrbitControls makeDefault enablePan maxPolarAngle={Math.PI / 2.15} minPolarAngle={0.25} minDistance={5} maxDistance={32} target={[0, 0.9, 0]} />
  </>;
}

export default function FactoryTwin({ site, sites = [], playing = true, severity }) {
  const siteKey = sites.map((s) => s.id).join('|');
  const profile = useMemo(() => profileForSite(site, sites), [site?.id, siteKey]); // eslint-disable-line react-hooks/exhaustive-deps
  const controller = useRef(null);
  if (!controller.current) controller.current = createLineController();
  const ctl = controller.current(site, severity);     // one robot carries the scenario
  const control = useRef(null);
  control.current = { ...ctl, playing };

  const [status, setStatus] = useState(null);
  useEffect(() => { setStatus(null); }, [profile]);

  const robots = site?.robots || [];
  const ids = (list) => list.map((i) => robots[i]?.id || `R${i + 1}`).join(', ');
  const issueOf = (i) => ISSUE_TEXT[ctl.robots[i]?.issue] || 'Fault';

  // per-robot tags
  const tags = profile.robots.map((_, i) => {
    const r = robots[i], c = ctl.robots[i];
    const id = r?.id || `R${i + 1}`;
    const tripped = status?.faulted.includes(i);
    const reading = c?.issue === 'thermal' || c?.issue === 'strain'
      ? (r?.temperature != null ? `${r.temperature}°C` : '')
      : c?.issue === 'bearing' ? (r?.vibration != null ? `${r.vibration} mm/s` : '') : '';
    if (tripped) return { id, tone: 'fault', headline: c?.issue === 'stopped' ? 'STOPPED' : 'PROTECTIVE STOP', detail: [ISSUE_TEXT[c?.issue] || 'Fault', reading].filter(Boolean).join(' · ') };
    if (c && ['bearing', 'thermal', 'strain'].includes(c.issue)) return { id, tone: 'warn', headline: c.trip ? 'FAULT DEVELOPING' : 'PREDICTIVE ALERT', detail: [ISSUE_TEXT[c.issue], reading].filter(Boolean).join(' · ') };
    if (c?.issue === 'quality' && c.defectRate >= 0.2) return { id, tone: 'warn', headline: 'QUALITY DRIFT', detail: 'Process out of tolerance' };
    return { id, tone: '' };
  });

  // line banner
  let banner = { tone: 'running', title: 'LINE RUNNING', detail: '' };
  if (status?.state === 'stopped') banner = { tone: 'stopped', title: 'LINE STOPPED', detail: `${ids(status.faulted)} ${issueOf(status.faulted[0]).toLowerCase()} · conveyor held by interlock` };
  else if (status?.state === 'paused') banner = { tone: 'paused', title: 'LINE PAUSED', detail: 'Feed hold · all motion stopped' };
  else if (status?.warnings.length) {
    const tripping = status.warnings.some((i) => ctl.robots[i]?.trip);
    banner = { tone: 'warning', title: tripping ? 'FAULT DEVELOPING' : 'PREDICTIVE ALERT', detail: `${ids(status.warnings)} ${issueOf(status.warnings[0]).toLowerCase()} · line still running` };
  } else if (site?.scenario === 'quality' && ctl.focus >= 0) banner = { tone: 'warning', title: 'QUALITY DRIFT', detail: `${ids([ctl.focus])} out of tolerance · defective parts flagged red and rejected` };
  else if (ctl.rate > 1.05) banner = { tone: 'surge', title: 'DEMAND SURGE', detail: `Line rate ${Math.round(ctl.rate * 100)}%` };

  return <div className="twin-canvas" role="img" aria-label={`Animated, orbitable 3D ${profile.line.toLowerCase()} for ${site?.name || 'the selected plant'}: six robots, an indexing conveyor and parts being built station by station.`}>
    <Canvas shadows dpr={[1, 1.65]} camera={{ position: [1.2, 7.4, 14.2], fov: 42, near: 0.1, far: 120 }} gl={{ antialias: true, alpha: false }}>
      <PlantScene profile={profile} control={control} onStatus={setStatus} tags={tags} />
    </Canvas>
    <div className="twin-overlay top"><span className="scope-dot" /> DIGITAL TWIN / {site?.id || 'PLANT'} <span className="small-label">{profile.line.toUpperCase()}</span></div>
    <div className={`twin-overlay line-status ${banner.tone}`} role="status">
      <strong><i />{banner.title}</strong>
      {banner.detail && <span>{banner.detail}</span>}
      {status && <span className="line-counts">GOOD {status.units} · REJECT {status.rejects} · CYCLE {status.cycle.toFixed(1)} s</span>}
    </div>
    <div className="twin-overlay bottom"><span>↻ Drag to orbit · Right-drag to pan · Scroll to zoom</span><span>{playing ? '● Kinematics active' : 'Ⅱ Motion paused'}</span></div>
  </div>;
}
