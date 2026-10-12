import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  Copy,
  FileSearch,
  Loader2,
  X,
} from "lucide-react";
import type { JsonObject, JsonValue } from "../../api/types";
import { humanize, display, safeUrl } from "../../utils/presentation";
export function Badge({
  children,
  tone = "",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function Status({ value }: { value?: string }) {
  const tone =
    value && /^(ok|ready|complete|completed|verified)$/i.test(value)
      ? "positive"
      : value && /missing|error|failed|unavailable/i.test(value)
        ? "negative"
        : "warning";
  return (
    <span className={`status ${value ? tone : ""}`}>
      <i />
      {value ? humanize(value) : "Unknown"}
    </span>
  );
}
export function PageHeader({
  eyebrow = "Intelligence workspace",
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action && <div className="header-actions">{action}</div>}
    </div>
  );
}
export function Panel({
  title,
  aside,
  children,
  className = "",
}: {
  title: string;
  aside?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-heading">
        <h2>{title}</h2>
        {aside}
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}
export function EmptyState({
  title,
  description,
  action,
  compact = false,
}: {
  title: string;
  description: string;
  action?: ReactNode;
  compact?: boolean;
}) {
  return (
    <div className={`empty-state ${compact ? "compact" : ""}`}>
      <div className="empty-icon">
        <FileSearch size={24} strokeWidth={1.3} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function ErrorState({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div className="error-state" role="alert">
      <AlertCircle size={18} />
      <div>
        <strong>Request unsuccessful</strong>
        <p>{message}</p>
      </div>
      {retry && (
        <button className="button secondary small" onClick={retry}>
          Retry
        </button>
      )}
    </div>
  );
}
export function Loading({
  label = "Waiting for the API response…",
}: {
  label?: string;
}) {
  return (
    <div className="loading" role="status">
      <Loader2 className="spin" size={19} />
      {label}
    </div>
  );
}
export function Metadata({
  data,
}: {
  data: JsonObject | Record<string, unknown>;
}) {
  return (
    <dl className="metadata">
      {Object.entries(data).map(([key, value]) => (
        <div key={key}>
          <dt>{humanize(key)}</dt>
          <dd>{display(value)}</dd>
        </div>
      ))}
    </dl>
  );
}
export function RawDetails({
  data,
  title = "Returned metadata",
}: {
  data: JsonValue | Record<string, unknown> | object;
  title?: string;
}) {
  return (
    <details className="raw-details">
      <summary>{title}</summary>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </details>
  );
}
export function SourceLink({
  url,
  children,
}: {
  url: unknown;
  children?: ReactNode;
}) {
  const href = safeUrl(url);
  return href ? (
    <a
      className="source-link"
      href={href}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children || new URL(href).hostname}
      <ArrowUpRight size={13} />
    </a>
  ) : (
    <span className="muted">{children || "URL not returned"}</span>
  );
}
export function CopyButton({ value }: { value: string }) {
  const [state, setState] = useState("");
  return (
    <button
      className="button secondary small"
      aria-label={`Copy ${value}`}
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setState("Copied");
        } catch {
          setState("Copy unavailable");
        }
      }}
    >
      <Copy size={13} />
      {state || "Copy"}
    </button>
  );
}
export function Drawer({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    function key(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
      if (e.key === "Tab") {
        const elements = ref.current?.querySelectorAll<HTMLElement>(
          'button,a[href],input,select,textarea,[tabindex="0"]',
        );
        if (!elements?.length) {
          e.preventDefault();
          return;
        }
        const first = elements[0],
          last = elements[elements.length - 1];
        if (
          e.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === ref.current)
        ) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [onClose]);
  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        ref={ref}
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawer-heading">
          <h2>{title}</h2>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close details"
          >
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
