# watsonx Orchestrate Embedded Chat

Embedded chat is the website-facing channel for a deployed Orchestrate agent.

```text
User browser -> embedded chat widget -> watsonx Orchestrate agent runtime
Website backend -> signs JWT / refreshes auth / enforces app auth
Agent runtime -> tools / collaborators / knowledge bases / connections
```

## Embedded chat vs REST `/runs`

Use embedded chat when the desired UX is a chat widget or chat panel inside an external web application.
Choose embedded chat when:

- A traditional small chat widget that hides/displays in the bottom-right is acceptable or preferred.
- A full screen chat interface is not required/desired
- Quick implementation is preferred over customization

Choose REST `/runs` when:

- The user interaction benefits from a full page layout.
- You want control over the layout which comes with the complexity of managing everything. need custom orchestration around run creation, streaming, polling, cancellation, or state.
- You want backend-only control over all agent interaction.

For REST-based chat development refer to the REST section of the [agents guide](agents.md) to learn how to Use direct REST `/runs` APIs to build a fully custom, often full screen chat UI.

## Prerequisites

1. Agent exists and has been imported.
2. Agent is deployed to live for production website use.
3. Embedded chat security is configured.
4. Required cryptographic keys are generated/uploaded.
5. Website backend can create/refresh signed JWTs.
6. Embed script is generated with the ADK CLI.


### Generate embed script:

```bash
orchestrate channels webchat embed --agent-name support_agent
```

The command outputs a `<script>` block containing values such as:

```javascript
window.wxOConfiguration = {
  orchestrationID: "your-orgID_orchestrationID",
  hostURL: "https://dl.watson-orchestrate.ibm.com", // or region-specific host
  rootElementID: "root",
  showLauncher: false,
  deploymentPlatform: "ibmcloud",
  crn: "your-org-crn",
  chatOptions: {
    agentId: "your-agent-id",
    agentEnvironmentId: "your-agent-env-id",
  },
};
```

Important:

- Use the agent **ID** and agent **environment ID** in runtime config, not just the agent name.
- Place the embed script inside `<body>` so the DOM and root element exist before initialization.
- For production embeds, loader path typically includes `/wxochat/wxoLoader.js?embed=true`.

Minimal page:

```html
<!doctype html>
<html lang="en">
  <body>
    <div id="root"></div>
    <script src="/embed/support-agent-webchat.js"></script>
  </body>
</html>
```

## Security architecture

Security is enabled by default, but must be configured explicitly. The embedded chat will not initialize unless the required cryptographic keys are configured and validated by the service.

Rules:

- Generate JWTs server-side only.
- Never expose private keys to the browser.
- Never hard-code API keys, JWT private keys, tenant IDs, or secrets into frontend code.
- Use HTTPS in production.
- Use short JWT expiration and refresh through `authTokenNeeded`.
- Use secure, HTTP-only cookies for stable anonymous IDs or authenticated session IDs.
- Put app authorization logic in the website backend, not in the browser.

Generate RSA keys for JWT signing:

```bash
# Option 1: ssh-keygen + openssl
ssh-keygen -t rsa -b 4096 -m PEM -f keys/example-jwtRS256.key
openssl rsa -in keys/example-jwtRS256.key -pubout -outform PEM -out keys/example-jwtRS256.key.pub

# Option 2: openssl only
openssl genrsa -out keys/example-jwtRS256.key 4096
openssl rsa -in keys/example-jwtRS256.key -pubout -out keys/example-jwtRS256.key.pub
```

Reference project layout:

```text
webchat_project/
├── keys/
│   ├── example-jwtRS256.key
│   ├── example-jwtRS256.key.pub
│   └── ibmPublic.key.pub
├── routes/
│   └── create_jwt.js
├── static/
│   └── index.html
├── server.js
└── package.json
```

## Backend JWT endpoint

The browser should call your backend for a signed token before initializing chat. The backend signs the token with your private key and may encrypt `user_payload` with IBM's public key.

```javascript
// routes/create_jwt.js
const fs = require("fs");
const path = require("path");
const express = require("express");
const jwt = require("jsonwebtoken");
const { v4: uuid } = require("uuid");

const router = express.Router();
const PRIVATE_KEY = fs.readFileSync(path.join(__dirname, "../keys/example-jwtRS256.key"));
const COOKIE_NAME = "ANONYMOUS_USER_ID";
const COOKIE_AGE_MS = 45 * 24 * 60 * 60 * 1000;

function getOrSetAnonymousId(req, res) {
  let anonymousId = req.cookies?.[COOKIE_NAME];
  if (!anonymousId) anonymousId = `anon-${uuid()}`;

  res.cookie(COOKIE_NAME, anonymousId, {
    expires: new Date(Date.now() + COOKIE_AGE_MS),
    httpOnly: true,
    sameSite: "Lax",
    secure: process.env.NODE_ENV === "production",
  });

  return anonymousId;
}

function createJwt(req, res) {
  const anonymousId = getOrSetAnonymousId(req, res);

  // Replace these values with your app's authenticated session/user data.
  const claims = {
    sub: req.user?.id || anonymousId,
    user_payload: {
      name: req.user?.displayName || "Anonymous",
      custom_user_id: req.user?.id || anonymousId,
      sso_token: req.user?.ssoToken,
    },
    context: {
      clientID: req.user?.tenantId || "anonymous_tenant",
      user_name: req.user?.displayName || "Anonymous",
      user_role: req.user?.role || "Guest",
    },
  };

  const token = jwt.sign(claims, PRIVATE_KEY, {
    algorithm: "RS256",
    expiresIn: "15m",
  });

  res.type("text/plain").send(token);
}

router.get("/", createJwt);
module.exports = router;
```

Server wiring:

```javascript
// server.js
const express = require("express");
const cookieParser = require("cookie-parser");
const createJwt = require("./routes/create_jwt");

const app = express();
app.use(cookieParser());
app.use("/createJWT", createJwt);
app.use(express.static("static"));
app.listen(process.env.PORT || 3000);
```

## Client initialization with token

Fetch a JWT, assign it to `window.wxOConfiguration.token`, then load the widget.

```html
<div id="root"></div>
<script>
  async function getIdentityToken() {
    const result = await fetch("/createJWT", { credentials: "include" });
    window.wxOConfiguration.token = await result.text();
  }

  function onChatLoad(instance) {
    window.wxoChatInstance = instance;

    instance.on("authTokenNeeded", async (event) => {
      const result = await fetch("/createJWT", { credentials: "include" });
      event.authToken = await result.text();
    });
  }

  window.wxOConfiguration = {
    orchestrationID: "your-orchestration-id",
    hostURL: "https://us-south.watson-orchestrate.cloud.ibm.com",
    rootElementID: "root",
    deploymentPlatform: "ibmcloud",
    crn: "your-crn",
    showLauncher: true,
    chatOptions: {
      agentId: "your-agent-id",
      agentEnvironmentId: "your-agent-environment-id",
      onLoad: onChatLoad,
    },
  };

  getIdentityToken().then(() => {
    const script = document.createElement("script");
    script.src = `${window.wxOConfiguration.hostURL}/wxochat/wxoLoader.js?embed=true`;
    script.addEventListener("load", () => wxoLoader.init());
    document.head.appendChild(script);
  });
</script>
```

## Context variables

Context variables pass website/user/application context into the agent runtime.

Two supported patterns:

| Method | Use when |
|---|---|
| JWT `context` claim | Stable identity/session values: tenant, role, user ID, permissions. |
| `pre:send` event | Dynamic per-message values: page, selected record, cart state, UI context. |

Agent YAML must opt in:

```yaml
spec_version: v1
kind: native
name: support_agent
style: react
llm: groq/openai/gpt-oss-120b
context_access_enabled: true
context_variables:
  - clientID
  - user_name
  - user_role
  - current_page
  - selected_record_id
instructions: |
  You have access to these context values:
  - clientID: {clientID}
  - user_name: {user_name}
  - user_role: {user_role}
  - current_page: {current_page}
  - selected_record_id: {selected_record_id}

  Do not ask the user for these values; they are provided by the application.
```

Rules:

- Do not use the `wxo_` prefix for custom variables; it is reserved for system variables.
- If the same variable appears in the JWT and `pre:send`, the JWT value wins.
- Use different names for stable JWT context and dynamic per-message context when both are needed.

Inject dynamic context with `pre:send`:

```javascript
function onChatLoad(instance) {
  instance.on("pre:send", (event) => {
    event.message.context = {
      ...(event.message.context || {}),
      current_page: window.location.pathname,
      selected_record_id: window.appState?.selectedRecordId,
    };
  });
}
```

## Instance methods

Instance methods let the application control an active chat instance after initialization.

Common methods:

| Method | Use |
|---|---|
| `instance.on(event, handler)` | Subscribe to repeated events. |
| `instance.once(event, handler)` | Subscribe once, then auto-remove. |
| `instance.off(event, handler)` | Remove an event handler. |
| `instance.send(message, options)` | Send a message programmatically. |
| `instance.restartConversation()` | Restart the current conversation. |
| `instance.loadThreadById(threadId)` | Load an existing thread. |
| `instance.updateAuthToken(token)` | Replace the current JWT. |
| `instance.changeView(viewState)` | Change the widget view state. |
| `instance.updateLocale(locale)` | Change display language. |
| `instance.updateWelcomeScreen(config)` | Change welcome message/starter prompts. |
| `instance.updateCustomHeaderItems(items)` | Add/update custom header actions. |
| `instance.destroy()` | Destroy and remove the chat instance. |

Programmatic send:

```javascript
window.wxoChatInstance.send("Show my open cases", { silent: false });
```

Silent system message:

```javascript
window.wxoChatInstance.send("User viewed product SKU-123", { silent: true });
```

Locale switcher:

```javascript
function onChatLoad(instance) {
  instance.updateCustomHeaderItems([
    {
      id: "language-selector",
      text: "Language",
      type: "dropdown",
      items: [
        { id: "lang-en", text: "English", onClick: () => instance.updateLocale("en") },
        { id: "lang-es", text: "Español", onClick: () => instance.updateLocale("es") },
      ],
    },
  ]);
}
```

## Events

Use events to intercept, transform, observe, or extend chat behavior.

| Category | Events |
|---|---|
| Lifecycle | `chat:ready` |
| Message | `pre:send`, `send`, `pre:stream:delta`, `pre:receive`, `receive` |
| Conversation | `pre:restartConversation`, `restartConversation`, `pre:threadLoaded` |
| Customization | `userDefinedResponse`, `customEvent` |
| Feedback | `feedback` |
| Security | `authTokenNeeded` |
| View | `view:pre:change`, `view:change`, `view:properties:pre:change`, `view:properties:change` |

Event handler pattern:

```javascript
function onChatLoad(instance) {
  instance.on("chat:ready", (event) => {
    console.log("chat ready", event);
  });

  instance.on("pre:send", (event) => {
    // Modify outgoing user message or attach dynamic context.
    event.message.context = {
      ...(event.message.context || {}),
      current_page: window.location.pathname,
    };
  });

  instance.on("pre:receive", (event) => {
    // Modify response before rendering.
    const lastItem = event?.message?.content?.[event.message.content.length - 1];
    if (lastItem?.text) {
      lastItem.text = lastItem.text.replace(/assistant/gi, "agent");
    }
  });

  instance.on("pre:stream:delta", (event) => {
    // Filter streaming deltas before rendering.
    event?.delta?.content?.forEach((item) => {
      if (item.response_type === "text" && item.text) {
        item.text = item.text.replace(/confidential/gi, "[REDACTED]");
      }
    });
  });

  instance.on("authTokenNeeded", async (event) => {
    const token = await fetch("/createJWT", { credentials: "include" }).then((r) => r.text());
    event.authToken = token;
  });
}
```

Best practices:

- Use `once()` for one-time setup.
- Use `off()` to remove unused handlers and avoid leaks.
- Keep event handlers lightweight and non-blocking.
- Wrap event logic in `try/catch` so UI does not break.
- Use `pre:*` events when you need to modify data before rendering/sending.
- Use `send`, `receive`, and `view:change` for analytics.

## Custom UI content

Use `userDefinedResponse` to render specialized response types in the host application.

```javascript
function onChatLoad(instance) {
  instance.on("userDefinedResponse", (event) => {
    event.hostElement.innerHTML = `
      <div class="custom-agent-card">
        <h4>Custom Response</h4>
        <p>${event.contentItem?.text || ""}</p>
      </div>
    `;
  });
}
```

Rules:

- Sanitize any HTML content before injecting into the DOM.
- Prefer framework rendering/portals for complex UI.
- Keep custom response schemas explicit in agent/tool instructions.

## Feedback controls

Thumbs-up/down feedback is enabled by default and stored by watsonx Orchestrate.

Customize feedback options:

```javascript
function preReceiveHandler(event) {
  const lastItem = event?.message?.content?.[event.message.content.length - 1];
  if (!lastItem) return;

  lastItem.message_options = {
    feedback: {
      is_on: true,
      show_positive_details: false,
      show_negative_details: true,
      positive_options: {
        categories: ["Helpful", "Accurate", "Clear", "Complete"],
        disclaimer: "Your feedback helps us improve.",
      },
      negative_options: {
        categories: ["Inaccurate", "Incomplete", "Too long", "Irrelevant", "Other"],
        disclaimer: "Please provide specific details.",
      },
    },
  };
}

function onChatLoad(instance) {
  instance.on("pre:receive", preReceiveHandler);
  instance.on("feedback", (event) => {
    console.log("feedback", event);
    // Optional: duplicate to analytics/custom storage.
  });
}
```

Disable feedback fully:

```javascript
function disableFeedbackOnMessage(message) {
  const lastItem = message?.content?.[message.content.length - 1];
  if (lastItem) {
    lastItem.message_options = { feedback: { is_on: false } };
  }
}

function onChatLoad(instance) {
  instance.on("pre:receive", (event) => disableFeedbackOnMessage(event.message));
  instance.on("pre:threadLoaded", (event) => {
    event.messages?.forEach(disableFeedbackOnMessage);
  });
}
```

Both `pre:receive` and `pre:threadLoaded` are required to disable feedback for new and restored historical messages.

When duplicating feedback to custom storage:

- Send asynchronously.
- Do not block the UI.
- Encrypt data in transit and at rest.
- Apply retention and consent policies.
- Remember that feedback may reflect application-modified response text, not only original agent output.

## UI customization

Add UI customization under `window.wxOConfiguration`.

Header:

```javascript
header: {
  showResetButton: true,
  showAiDisclaimer: true,
  showMaximize: false,
  showAgentAvatar: false,
  showAgentName: false,
}
```

Features:

```javascript
features: {
  showThreadList: true,
  showAgentMemory: true,
}
```

Language:

```javascript
defaultLocale: "en" // en, es, fr, de, it, ja, ko, pt-BR, zh-CN, zh-TW
```

Style:

```javascript
style: {
  headerColor: "#0f62fe",
  userMessageBackgroundColor: "#e8f0ff",
  primaryColor: "#0f62fe",
  fontFamily: "IBM Plex Sans",
  showBackgroundGradient: true,
}
```

Layout:

```javascript
layout: {
  form: "float", // commonly float, fullscreen-overlay, or custom depending on deployment
}
```

Guidance:

- `showThreadList` defaults vary by layout; set explicitly for predictable behavior.
- `showLauncher` controls initial launcher visibility for fullscreen-overlay behavior.
- Use `changeView()` for runtime layout/view changes.
- Use supported locale codes only.
- 
## Debugging checklist

1. Agent is imported and deployed to live.
2. Embed script was generated for the correct agent.
3. Runtime config uses `agentId` and `agentEnvironmentId`, not only agent name.
4. `hostURL`, `orchestrationID`, `deploymentPlatform`, and `crn` match the target environment.
5. `<div id="root"></div>` exists before loader initialization.
6. Security keys are configured in Orchestrate.
7. Backend `/createJWT` returns a valid RS256 token.
8. Private key is server-side only.
9. `authTokenNeeded` refreshes expired tokens.
10. Browser console has no CORS, CSP, or loader errors.
11. Event handlers do not throw uncaught exceptions.
12. Context variable names match the agent YAML.
13. No custom variable uses the reserved `wxo_` prefix.
14. If feedback is disabled, both `pre:receive` and `pre:threadLoaded` handlers are registered.

## Model guidance

When generating embedded chat code:

1. Create a backend JWT endpoint; never generate JWTs in browser code.
2. Use the CLI-generated embed config as the source of truth for IDs and host values.
3. Include `authTokenNeeded` token refresh.
4. Add context variables explicitly to agent YAML before using them in web chat.
5. Use `pre:send` for dynamic page-level context.
6. Use `userDefinedResponse` only when the agent/tool response schema requires custom rendering.
7. Prefer small, composable event handlers.
8. Keep website security, authorization, and secret handling on the backend.
