import { apiFetch } from "../api";

const sendMessage = async () => {
  try {
    const data = await apiFetch("/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });

    setMessages((m) => [...m, { role: "assistant", text: data.reply }]);
  } catch (e) {
    setError("Please login as a hiring manager");
  }
};
