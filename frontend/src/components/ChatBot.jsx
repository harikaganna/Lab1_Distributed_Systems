import React, { useState } from "react";
import { api } from "../api/axios";
import { useSelector } from "react-redux";
import { selectUser } from "../store/slices/authSlice";
import { Link } from "react-router-dom";

export default function ChatBot() {
  const user = useSelector(selectUser);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!user) return null;

  const sendMessage = async (text) => {
    const msg = text || input;
    if (!msg.trim()) return;
    const userMsg = { role: "user", content: msg };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/ai-assistant/chat", {
        message: msg,
        conversation_history: updated,
      });
      setMessages([...updated, { role: "assistant", content: res.data.response, recommendations: res.data.recommendations }]);
    } catch {
      setMessages([...updated, { role: "assistant", content: "Sorry, something went wrong. Try again." }]);
    }
    setLoading(false);
  };

  const clearChat = () => setMessages([]);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="btn btn-brand rounded-circle shadow"
        style={{ position: "fixed", bottom: 24, right: 24, width: 56, height: 56, fontSize: 24, zIndex: 1000 }}
      >
        💬
      </button>

      {open && (
        <div className="card card-clean shadow" style={{ position: "fixed", bottom: 90, right: 24, width: 380, maxWidth: "calc(100vw - 32px)", height: 500, zIndex: 1000, display: "flex", flexDirection: "column" }}>
          <div className="card-header d-flex justify-content-between align-items-center">
            <strong>AI Assistant</strong>
            <div>
              <button className="btn btn-sm btn-soft me-1" onClick={clearChat}>Clear</button>
              <button className="btn btn-sm btn-outline-secondary" onClick={() => setOpen(false)}>✕</button>
            </div>
          </div>

          <div className="card-body" style={{ flex: 1, overflowY: "auto", fontSize: "0.9rem" }}>
            {messages.length === 0 && (
              <div className="text-muted text-center mt-4">
                <p>Ask me for restaurant recommendations!</p>
                <div className="d-flex flex-wrap gap-1 justify-content-center">
                  {["Find dinner tonight", "Best rated near me", "Vegan options"].map((q) => (
                    <button key={q} className="btn btn-sm btn-soft" onClick={() => sendMessage(q)}>{q}</button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`mb-2 ${msg.role === "user" ? "text-end" : ""}`}>
                <div className={`d-inline-block p-2 rounded-3 ${msg.role === "user" ? "bg-opacity-10" : "bg-light"}`}
                     style={{ maxWidth: "85%", textAlign: "left", background: msg.role === "user" ? "rgba(107,63,160,0.1)" : undefined }}>
                  {msg.content}
                  {msg.recommendations?.length > 0 && (
                    <div className="mt-2">
                      {msg.recommendations.map((r) => (
                        <Link key={r.id} to={`/restaurants/${r.id}`} onClick={() => setOpen(false)}
                              className="d-block p-2 mb-1 rounded text-decoration-none"
                              style={{ background: "rgba(107,63,160,0.06)", border: "1px solid rgba(107,63,160,0.15)" }}>
                          <div className="d-flex justify-content-between align-items-center">
                            <strong style={{ color: "var(--brand)", fontSize: "0.85rem" }}>{r.name}</strong>
                            {r.rating && <span className="badge badge-soft" style={{ fontSize: "0.75rem" }}>{r.rating}★</span>}
                          </div>
                          <div className="small text-muted">
                            {r.cuisine ? r.cuisine.charAt(0).toUpperCase() + r.cuisine.slice(1) : ""}{r.price ? ` · ${r.price}` : ""}{r.city ? ` · ${r.city}` : ""}
                          </div>
                          {r.description && (
                            <div className="small mt-1" style={{ color: "var(--text-secondary, #555)" }}>
                              {r.description}
                            </div>
                          )}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && <div className="text-muted small">Thinking...</div>}
          </div>

          <div className="card-footer p-2">
            <div className="input-group">
              <input className="form-control form-control-sm" placeholder="Ask me anything..."
                     value={input} onChange={(e) => setInput(e.target.value)}
                     onKeyDown={(e) => e.key === "Enter" && sendMessage()} />
              <button className="btn btn-sm btn-brand" onClick={() => sendMessage()} disabled={loading}>Send</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
