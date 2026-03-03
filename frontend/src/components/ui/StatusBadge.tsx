interface StatusBadgeProps {
  status: "pass" | "fail" | "warning" | "unknown";
  size?: "sm" | "md";
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const baseClass = "badge";
  const statusClass = `badge-${status}`;
  const sizeClass = size === "sm" ? "text-xs" : "text-sm";

  return <span className={`${baseClass} ${statusClass} ${sizeClass}`}>{status}</span>;
}
