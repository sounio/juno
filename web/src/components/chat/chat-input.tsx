"use client";

import { useState, useRef, useEffect } from "react";

export function ChatInput({
  onSend,
  onStop,
  isLoading,
}: {
  onSend: (content: string) => void;
  onStop?: () => void;
  isLoading: boolean;
}) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
    }
  }, [input]);

  useEffect(() => {
    if (!isLoading) textareaRef.current?.focus();
  }, [isLoading]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-neutral-800 p-4">
      <div className="max-w-3xl mx-auto flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message Juno..."
          rows={1}
          disabled={isLoading}
          className="flex-1 bg-neutral-800 text-neutral-100 placeholder-neutral-500 rounded-xl px-4 py-2.5 text-sm resize-none outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
        {isLoading ? (
          <button
            onClick={onStop}
            className="bg-red-600 hover:bg-red-500 text-white rounded-xl px-4 py-2.5 transition-colors"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="1" />
            </svg>
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white rounded-xl px-4 py-2.5 transition-colors disabled:text-neutral-500"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
