# Application Performance — Bob Custom Modes

This directory contains custom Bob modes for the Application Performance building block.

---

## 📦 Available Modes

### Application Performance

A custom Bob mode that equips Bob with the knowledge and workflows to:

- Build, configure, and operate IBM Turbonomic resource optimization dashboards.
- Connect to Turbonomic REST API v3 for topology discovery, market data, and telemetry.
- Execute and automate resource actions (resizing, provisioning, scaling, moving) across VMs and containers.
- Monitor application performance metrics and Kubernetes cluster capacity.

| Property | Value |
|---|---|
| Mode zip | `base-modes/automated-resource-mgmt.zip` |
| Requires | IBM Turbonomic API access + Bob UI |

---

## 🚀 Installation

See the step-by-step installation guide in [`base-modes/README.md`](base-modes/README.md) for instructions on importing this mode into a new or existing Bob project.

---

## 🔧 Requirements

- Bob UI with custom modes support
- IBM Turbonomic v8.x+ instance with API access
- Python 3.10+ for local dashboard testing

---

## 🔗 Related

- [Bob Skills for Application Performance](../bob-skills/README.md) — skills that complement these modes
- [Automated Resource Management Asset](../assets/automated-resource-mgmt/README.md) — Dashboard application implementation
- [Parent Directory README](../README.md) — building block overview and architecture
