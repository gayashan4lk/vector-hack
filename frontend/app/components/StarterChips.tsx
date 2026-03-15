"use client";

import { Sparkles } from "lucide-react";

const STARTER_QUERIES = [
  "Is Vector Agents competitive in the AI SDR market right now?",
  "Is the digital workers category accelerating or consolidating?",
  "What should Vector Agents build or reposition over the next six months?",
];

interface StarterChipsProps {
  onSelect: (query: string) => void;
}

export default function StarterChips({ onSelect }: StarterChipsProps) {
  return (
    <div className="flex flex-col items-center gap-6 py-16">
      <div className="flex items-center gap-2 text-zinc-400">
        <Sparkles className="h-5 w-5" />
        <span className="text-sm font-medium">Try a starter question</span>
      </div>
      <div className="flex flex-col gap-3 w-full max-w-lg">
        {STARTER_QUERIES.map((query) => (
          <button
            key={query}
            type="button"
            onClick={() => onSelect(query)}
            className="rounded-xl border border-zinc-700 bg-zinc-800/50 px-4 py-3 text-left text-sm text-zinc-300 transition-colors hover:border-zinc-500 hover:bg-zinc-800 hover:text-zinc-100"
          >
            {query}
          </button>
        ))}
      </div>
    </div>
  );
}
