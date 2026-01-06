import { api } from "./client";

export type ChatMsg = { role: "user" | "assistant"; content: string };

export async function sendChat(messages: { role: string; content: string }[]) {
  return api("/chat", {
    method: "POST",
    body: JSON.stringify({ messages }),
  });
}
