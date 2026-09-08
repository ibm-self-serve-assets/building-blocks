# Maximo Code Modernization Asset

Full-stack web application for IBM Maximo code modernization — AI-powered automation script optimization and Java-to-automation-script conversion.

**Stack**: Node.js (Express) backend + React (Vite) frontend
**Port**: Backend `5000` · Frontend `3000` (dev) / `8080` (Docker)

---

## Features

| Capability | Description |
|---|---|
| **Script Optimization** | Fetch, analyse, and AI-optimise Maximo automation scripts via `MXAPIAUTOSCRIPT` |
| **Java Code Conversion** | Convert Maximo Java classes to Python (Jython), JavaScript, Nashorn, ECMAScript, or MBR |
| **Batch Conversion** | Convert multiple Java files in a single operation |
| **Impact Analysis** | Dependency graph and risk assessment for any script before modifying it in production |
| **Best Practices** | Automatic enforcement of security, performance, and coding standards on every operation |
| **Push Back to Maximo** | Write optimised scripts directly back to Maximo via REST `PUT` |

---

## Prerequisites

- Node.js v14+
- npm
- IBM Maximo Application Suite instance with REST API access enabled
- Maximo API key — generate in MAS → Security → API Keys
- OpenAI API key — for AI-powered script optimisation ([platform.openai.com](https://platform.openai.com/api-keys))

---

## Quick Start

### 1. Configure the backend

```bash
cd backend
cp .env.template .env
```

Edit `backend/.env`:

```env
PORT=5000
NODE_ENV=development
MAXIMO_BASE_URL=https://your-maximo-server.com
MAXIMO_API_ENDPOINT=/maximo/api/os/MXAPIAUTOSCRIPT?oslc.pageSize=1000&oslc.select=*
MAXIMO_API_KEY=your-maximo-api-key
OPENAI_API_KEY=your-openai-api-key
CORS_ORIGIN=http://localhost:3000
```

### 2. Install dependencies and start both servers

```bash
# Terminal 1 — backend
cd backend
npm install
npm start
# API → http://localhost:5000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
# UI → http://localhost:3000
```

### 3. Connect to Maximo

Open `http://localhost:3000` → navigate to **Maximo Configuration** → enter your server URL and API key → click **Test Connection**.

---

## Usage

### Script Optimization

1. From the **Dashboard**, review the script count and language breakdown
2. Navigate to **Script List** to browse all automation scripts fetched from Maximo
3. Select a script → click **Analyse** to view security, performance, and quality issues
4. Click **Optimise** to generate an AI-powered optimised version with before/after comparison
5. Review the report then click **Push to Maximo** to write the optimised script back

### Java Code Conversion

1. Navigate to **Code Conversion**
2. Paste or upload a Java class source file
3. Select the target language (Python, Jython, JavaScript, Nashorn, ECMAScript, or MBR)
4. Click **Convert** — the converted script and a test script are generated side by side
5. Review the conversion report then click **Create in Maximo** to push the new script

### Batch Code Conversion

1. Navigate to **Batch Code Conversion**
2. Upload multiple `.java` files
3. Select the target language
4. Click **Convert All** — progress is tracked in real time
5. Download results or create all scripts in Maximo in bulk

---

## Backend API Reference

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Server health check |

### Script Optimization

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/scripts` | List all automation scripts from Maximo |
| `GET` | `/api/scripts/statistics` | Script count, language breakdown, issue summary |
| `GET` | `/api/scripts/analyze` | Analyse all scripts for issues |
| `GET` | `/api/scripts/:name` | Get a single script |
| `GET` | `/api/scripts/:name/analyze` | Analyse a single script |
| `GET` | `/api/scripts/:name/impact` | Impact analysis — dependencies and risk |
| `GET` | `/api/scripts/:name/optimize` | AI-powered optimisation with GPT-4 |
| `POST` | `/api/scripts/:name/update` | Push optimised script back to Maximo |

### Code Conversion

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/conversion/languages` | List supported target languages |
| `POST` | `/api/conversion/convert` | Convert Java code to automation script |
| `POST` | `/api/conversion/test` | Test a converted script |
| `POST` | `/api/conversion/create` | Create a converted script in Maximo |
| `POST` | `/api/conversion/batch` | Start a batch conversion job |
| `GET` | `/api/conversion/batch/:batchId/status` | Poll batch job status |
| `GET` | `/api/conversion/batch/:batchId/results` | Retrieve batch results |
| `GET` | `/api/conversion/history` | Conversion history |

### Connection

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/connection/test` | Test Maximo connectivity |

### Response format

```json
// Success
{ "success": true, "data": { ... } }

// Error
{ "success": false, "message": "Error description" }
```

---

## Supported Target Languages

| Language | Engine | Version |
|---|---|---|
| Python (Jython) | Jython | 2.7.4 |
| JavaScript | Nashorn | 15.6 |
| Nashorn | Nashorn | 15.6 |
| ECMAScript | Nashorn | 15.6 |
| Maximo Business Rules (MBR) | MBR | 1.0 |

---

## Project Structure

```
maximo_code_modernization_asset/
├── backend/
│   ├── src/
│   │   ├── controllers/              # Request handlers
│   │   │   ├── connectionController.js
│   │   │   └── scriptController.js
│   │   ├── routes/                   # Express route definitions
│   │   │   ├── connectionRoutes.js
│   │   │   └── scriptRoutes.js
│   │   ├── services/                 # Business logic
│   │   │   ├── aiOptimizer.js        # GPT-4 optimisation
│   │   │   ├── codeConverter.js      # Java → script conversion
│   │   │   ├── impactAnalyzer.js     # Dependency & risk analysis
│   │   │   ├── maximoBestPractices.js
│   │   │   ├── maximoService.js      # Maximo REST API client
│   │   │   └── simpleConverter.js
│   │   └── server.js                 # Express entry point
│   ├── .env.template
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ScriptList.jsx
│   │   │   ├── ScriptAnalyzer.jsx
│   │   │   ├── ScriptOptimizer.jsx
│   │   │   ├── ScriptDetail.jsx
│   │   │   ├── CodeConversion.jsx
│   │   │   ├── BatchCodeConversion.jsx
│   │   │   ├── ImpactAnalysisView.jsx
│   │   │   ├── MaximoConfig.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Navigation.jsx
│   │   ├── services/
│   │   │   └── api.js                # Axios API client
│   │   ├── styles/
│   │   │   └── App.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .env.template
└── README.md                         # This file
```

### Frontend technologies

- **React 18** — component framework
- **Vite** — build tool with HMR
- **IBM Carbon Design System** (`@carbon/react`) — UI components
- **Axios** — HTTP client
- **Recharts** — data visualisations
- **React Syntax Highlighter** — code display

### Backend technologies

- **Node.js + Express** — API server
- **OpenAI SDK** — GPT-4 powered script optimisation
- **node-fetch / axios** — Maximo REST API calls

---

## Frontend Development

Add a new feature:

1. Create a component in `frontend/src/components/`
2. Add any required API calls in `frontend/src/services/api.js`
3. Add styles in `frontend/src/styles/App.css`
4. Import and wire up in `frontend/src/App.jsx`

Useful commands:

```bash
# Development server with HMR
npm run dev

# Production build
npm run build

# Preview production build locally
npm run preview
```

---

## Troubleshooting

**Port conflicts:**
```bash
# macOS / Linux
lsof -ti:3000,5000 | xargs kill -9
```

**Maximo connection issues:**
- Verify the Maximo URL is accessible from your machine
- Validate the API key in MAS → Security → API Keys
- Check network / VPN access

**OpenAI optimisation fails:**
- Verify `OPENAI_API_KEY` is set correctly in `backend/.env`
- Check your OpenAI account quota and billing status

**Frontend cannot reach backend:**
- Confirm the backend is running on port `5000`
- Check that `CORS_ORIGIN` in `backend/.env` matches the frontend URL
