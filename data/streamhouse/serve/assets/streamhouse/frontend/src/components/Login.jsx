import React, { useState } from 'react';
import { Button, TextInput, PasswordInput, InlineNotification } from '@carbon/react';
import { ArrowRight, Factory, Activity, RadioTower, Workflow, ShieldCheck } from 'lucide-react';
import { call } from '../sim/api.js';

export const SESSION_KEY = 'fp-session';
export const TOKEN_KEY = 'fp-token';
const DEFAULT_USER = 'admin';

const FEATURES = [
  { icon: Activity,     label: 'Real-time telemetry',   detail: '36 synthetic assets · 6 US plants' },
  { icon: RadioTower,   label: 'IBM Confluent Kafka',   detail: 'Durable event backbone · governed schemas' },
  { icon: Workflow,     label: 'Apache Flink SQL',       detail: 'Continuous streaming intelligence' },
  { icon: ShieldCheck,  label: 'Stream Governance',      detail: 'Lineage, discoverability & RTCE/MCP' },
];

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [busy, setBusy]         = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) { setError('Enter your username and password.'); return; }
    setBusy(true);
    setError('');
    try {
      const res = await call('login', { username: username.trim(), password });
      if (res.ok) {
        sessionStorage.setItem(SESSION_KEY, res.user || username.trim());
        if (res.token) sessionStorage.setItem(TOKEN_KEY, res.token);
        onSuccess(res.user || username.trim());
      } else {
        setError(res.error || 'Invalid username or password.');
      }
    } catch (err) {
      setError(err.message || 'Sign-in failed. Please check credentials.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-shell">
      {/* ── Left brand panel ── */}
      <div className="login-brand-panel">
        <div className="login-grid-bg" aria-hidden="true" />
        <div className="login-brand-content">
          <div className="login-logo-row">
            <div className="login-logo-mark">◈</div>
            <div className="login-logo-text">Factory<span>Pulse</span></div>
          </div>
          <p className="login-brand-tagline">
            IBM Confluent Streamhouse showcase.<br />
            Every factory signal — one intelligence layer.
          </p>
          <ul className="login-features">
            {FEATURES.map(({ icon: Icon, label, detail }) => (
              <li key={label}>
                <div className="login-feature-icon"><Icon size={18} /></div>
                <div>
                  <strong>{label}</strong>
                  <span>{detail}</span>
                </div>
              </li>
            ))}
          </ul>
          <div className="login-brand-badges">
            <span>IBM</span><span>Confluent</span><span>Apache Kafka</span><span>Apache Flink</span>
          </div>
        </div>
        <div className="login-brand-foot">Synthetic factory data · reference demonstration v1.0</div>
      </div>

      {/* ── Right form panel ── */}
      <div className="login-form-panel">
        <form className="login-card" onSubmit={submit} noValidate>
          <div className="login-card-eyebrow">MANUFACTURING COMMAND CENTER</div>
          <h1 className="login-card-title">Sign in</h1>
          <p className="login-card-sub">
            Access the live digital twin, streaming data pipelines and AI context layer.
          </p>

          {error && (
            <InlineNotification
              kind="error"
              lowContrast
              hideCloseButton
              title="Sign-in failed"
              subtitle={error}
              className="login-error"
            />
          )}

          <TextInput
            id="login-user"
            labelText="Username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <PasswordInput
            id="login-pass"
            labelText="Password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button
            type="submit"
            kind="primary"
            size="lg"
            renderIcon={ArrowRight}
            disabled={busy}
            className="login-submit"
          >
            {busy ? 'Signing in…' : 'Continue to Factory Pulse'}
          </Button>

          <div className="login-hint-row">
            <Factory size={13} />
            <span>Demo access · default user <code>{DEFAULT_USER}</code></span>
          </div>
        </form>

        <div className="login-form-foot">© 2026 Factory Pulse · IBM Confluent Streamhouse</div>
      </div>
    </div>
  );
}
