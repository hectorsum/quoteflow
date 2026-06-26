import { QuoteStatus } from "@/lib/api";
import { groupOf, labelOf, GROUP_META } from "@/lib/status";

export function StatusBadge({ status }: { status: QuoteStatus }) {
  const group = groupOf(status);
  const meta = GROUP_META[group];

  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
      style={{ backgroundColor: meta.badgeBg, color: meta.badgeText }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: meta.dot }} />
      {labelOf(status)}
    </span>
  );
}
