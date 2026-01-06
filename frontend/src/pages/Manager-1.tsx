import { api } from "../api/client";

const sendMessage = async (msg: string, setMessages: any, setError: any) => {
  try {
    const data = await api("/chat", {
      method: "POST",
      body: JSON.stringify({ messages: [{ role: "user", content: msg }] }),
    });
    setMessages((m: any[]) => [...m, { role: "assistant", text: data.reply }]);
  } catch (e) {
    setError && setError("Please login as a hiring manager");
  }
};
