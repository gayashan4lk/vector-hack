"use client";

import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import type { AgentStatus } from "../hooks/useChat";

interface AgentStatusPanelProps {
  statuses: AgentStatus[];
}

export default function AgentStatusPanel({ statuses }: AgentStatusPanelProps) {
  if (statuses.length === 0) return null;

  return (
    <div className="mx-4 mb-4 rounded-xl border border-zinc-700 bg-zinc-900 p-3">
      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
        Agent Activity
      </div>
      <div className="space-y-2">
        {statuses.map((status) => (
          <div
            key={status.agent_id}
            className="flex items-center gap-3 text-sm"
          >
            <StatusIcon status={status.status} />
            <span className="font-medium text-zinc-200">
              {formatAgentName(status.agent_id)}
            </span>
            <span className="text-zinc-400">{status.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "complete":
      return <CheckCircle2 className="h-4 w-4 text-green-400" />;
    case "failed":
    case "error":
      return <XCircle className="h-4 w-4 text-red-400" />;
    default:
      return <Loader2 className="h-4 w-4 animate-spin text-yellow-400" />;
  }
}

function formatAgentName(id: string): string {
  return id
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
