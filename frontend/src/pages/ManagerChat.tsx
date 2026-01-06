import { useState } from "react";
import { sendChat } from "../api/chat";

export default function ManagerChat() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  async function send() {
    if (!input.trim()) return;
    setMessages((m) => [...m, { role: "user", text: input }]);
    const text = input;
    setInput("");

    const res = await sendChat(text);
    setMessages((m) => [...m, { role: "assistant", text: res.reply }]);
  }

  return (
    <div className="card">
      <h2>Manager Copilot</h2>
      <div className="chat">
        {messages.map((m, i) => (
          <div key={i} className={m.role}>{m.text}</div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={send}>Send</button>
    </div>
  );
}
