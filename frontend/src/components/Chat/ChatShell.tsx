import { useEffect, useRef, useState } from "react";
import { sendChat } from "../../api/chat";

type Msg = { role: "user" | "assistant"; content: string };

export default function ChatShell() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content:
        "Hi! Ask me to create jobs (e.g., “Create a Backend Engineer role…”) or ask database questions (e.g., “How many applications per job?”).",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function onSend() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    const next = [...messages, { role: "user", content: text } as Msg];
    setMessages(next);
    setBusy(true);

    try {
      const payload = next
        .filter((m) => m.role !== "assistant" || m.content) // keep all
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await sendChat(payload);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card" style={{ height: "72vh", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h2 style={{ margin: 0 }}>Manager Copilot</h2>
        <span className="badge">Tool-using AI • Create Jobs • Query DB</span>
      </div>

      <div style={{ flex: 1, overflow: "auto", marginTop: 12, paddingRight: 6 }}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              justifyContent: m.role === "user" ? "flex-end" : "flex-start",
              marginBottom: 10,
            }}
          >
            <div
              style={{
                maxWidth: "78%",
                padding: "10px 12px",
                borderRadius: 14,
                background: m.role === "user" ? "rgba(120,160,255,0.22)" : "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.12)",
                whiteSpace: "pre-wrap",
                lineHeight: 1.35,
              }}
            >
              {m.content}
            </div>
          </div>
        ))}
        {busy && <div style={{ opacity: 0.7 }}>Thinking…</div>}
        <div ref={endRef} />
      </div>

      <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
        <input
          className="input"
          placeholder='Try: "Create a Data Analyst role, requirements ..., salary 1800000"'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSend()}
        />
        <button className="btn" onClick={onSend}>
          Send
        </button>
      </div>
    </div>
  );
}
