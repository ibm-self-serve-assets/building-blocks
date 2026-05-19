// Production-grade chat widget with guardrails wired into submit/receive events.
//
// Topology:
//   browser (this file) → /api/chat → guardrails service → IBM Cloud
//
// What this snippet does NOT do (deliberately):
//   - Does NOT call the guardrails REST endpoint directly. Browser → partner
//     backend → guardrails. The API key never reaches the browser.
//   - Does NOT persist audit data to localStorage. Audit lives server-side.
//   - Does NOT show which specific metric tripped on Block (adversarial intel).
//
// Pair with reference-payloads/backend_guardrails_proxy.py for the
// server-side counterpart that proxies to the guardrails service and
// runs the AuditLogger.

import React, { useCallback, useEffect, useRef, useState } from "react";

// Treat as opaque server-managed state. Don't store API keys or full audit
// records here — only what the UI needs to render.
const BACKEND_CHAT_ENDPOINT = "/api/chat";

export default function ChatWidget() {
  const [messages, setMessages] = useState([]); // [{role: "user"|"agent", text, action, request_id}]
  const [input, setInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [submitting]);

  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim()) return;

      // Correlation ID — generated once per user message, propagated to
      // backend → guardrails → audit log so we can join records later.
      const requestId = crypto.randomUUID();

      // Optimistically render the user's message
      setMessages((m) => [...m, { role: "user", text, request_id: requestId }]);
      setInput("");
      setSubmitting(true);

      try {
        const resp = await fetch(BACKEND_CHAT_ENDPOINT, {
          method: "POST",
          credentials: "include",                  // session cookie / JWT — never API key
          headers: {
            "Content-Type": "application/json",
            "X-Request-ID": requestId,
          },
          body: JSON.stringify({ query: text, request_id: requestId }),
        });

        if (!resp.ok) {
          // Backend should have already converted guardrail Blocks into 200
          // responses with a fallback_message. A non-200 here is an
          // unexpected failure (network, backend down, etc.) — fail-open or
          // fail-closed per the partner's policy. Here we fail-open with a
          // generic apology.
          setMessages((m) => [
            ...m,
            { role: "agent", text: "Sorry, something went wrong. Please try again.", action: "Error", request_id: requestId },
          ]);
          return;
        }

        const data = await resp.json();
        // Expected shape from backend:
        //   { action: "Pass" | "Flag" | "Block", text: "...", request_id: "..." }
        // - On Block: data.text is the fallback_message (do NOT expose metric details)
        // - On Flag: data.text is the agent response (optionally render a badge)
        // - On Pass: data.text is the agent response
        setMessages((m) => [
          ...m,
          {
            role: "agent",
            text: data.text,
            action: data.action,
            request_id: data.request_id || requestId,
          },
        ]);
      } catch (err) {
        // Network failure — apply the partner's failure-mode policy here
        setMessages((m) => [
          ...m,
          { role: "agent", text: "Sorry, I couldn't reach the service.", action: "Error", request_id: requestId },
        ]);
      } finally {
        setSubmitting(false);
      }
    },
    []
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (submitting) return;
    sendMessage(input);
  };

  return (
    <div className="chat-widget">
      <div className="chat-history">
        {messages.map((m, i) => (
          <Message key={`${m.request_id}-${i}`} message={m} />
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={submitting}
        />
        <button type="submit" disabled={submitting || !input.trim()}>
          {submitting ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

function Message({ message }) {
  const { role, text, action } = message;

  // UX-per-action rules:
  //   Pass  — render normally
  //   Flag  — render normally PLUS a subtle "flagged" badge (optional;
  //           many partners only surface this in the compliance dashboard,
  //           not to end users)
  //   Block — render the fallback_message; no metric details
  //   Error — render the generic apology; partner's fail-open/closed policy
  return (
    <div className={`chat-message chat-message-${role}`}>
      <div className="chat-message-text">{text}</div>
      {role === "agent" && action === "Flag" && (
        <span className="chat-message-badge" title="Flagged for review">
          {/* Use your design system. Subtle, not alarming. */}
          ⚠ flagged
        </span>
      )}
    </div>
  );
}
