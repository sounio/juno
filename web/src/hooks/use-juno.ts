"use client";

import { createWebSocket, apiPost } from "@/lib/api";
import { useState, useRef, useCallback, useEffect } from "react";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
}

export function useJuno() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const sessionIdRef = useRef<string>(crypto.randomUUID());

  const connect = useCallback(() => {
    const ws = createWebSocket();
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "response" && data.data?.metadata?.response) {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: data.data.metadata.response,
              timestamp: Date.now(),
            },
          ]);
          setIsLoading(false);
        }
      } catch {}
    };
    wsRef.current = ws;
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }));

      try {
        const result = await apiPost("/agent/chat", {
          messages: history,
          user_id: "web",
          device_id: "web",
        });
        if (result?.metadata?.response) {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: result.metadata.response,
              timestamp: Date.now(),
            },
          ]);
        }
      } catch (err) {
        console.error("Chat error:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [messages]
  );

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { messages, sendMessage, isLoading, isConnected, sessionId: sessionIdRef.current };
}
