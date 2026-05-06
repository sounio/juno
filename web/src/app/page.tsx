"use client";

import { useJuno } from "@/hooks/use-juno";
import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { Sidebar } from "@/components/layout/sidebar";
import { useState } from "react";

export default function Home() {
  const { messages, sendMessage, isLoading, stopGeneration } = useJuno();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-dvh bg-neutral-950 text-neutral-100">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        isConnected={true}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center gap-3 px-4 h-14 border-b border-neutral-800 shrink-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 hover:bg-neutral-800 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <span className="text-lg font-semibold tracking-tight">Juno</span>
          </div>
        </header>
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendMessage} onStop={stopGeneration} isLoading={isLoading} />
      </main>
    </div>
  );
}
