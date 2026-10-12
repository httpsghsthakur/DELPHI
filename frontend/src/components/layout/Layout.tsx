import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { NavLink, Link, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowUpRight,
  Bell,
  ChevronsLeft,
  ChevronsRight,
  Command,
  Menu,
  Search,
  X,
} from "lucide-react";
import { useAnalysisStore } from "../../state/analysisStore";
import { navigation } from "./navigation";
import { Drawer, Metadata, Status } from "../ui/Primitives";
export function Layout({ children }: { children: ReactNode }) {
  const sidebarRef = useRef<HTMLElement>(null);
  const [collapsed, setCollapsed] = useState(false),
    [mobileOpen, setMobileOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [dialog, setDialog] = useState<"notifications" | "application" | null>(
    null,
  );
  const closeDialog = useCallback(() => setDialog(null), []);
  const { systemStatus, healthError, refreshSystem, history } =
    useAnalysisStore();
  const location = useLocation(),
    navigate = useNavigate();
  useEffect(() => {
    void refreshSystem();
  }, [refreshSystem]);
  useEffect(() => {
    function shortcut(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        document.getElementById("global-search")?.focus();
      }
    }
    document.addEventListener("keydown", shortcut);
    return () => document.removeEventListener("keydown", shortcut);
  }, []);
  useEffect(() => {
    if (!mobileOpen) return;
    const previous = document.activeElement as HTMLElement | null;
    sidebarRef.current
      ?.querySelector<HTMLButtonElement>(".mobile-close")
      ?.focus();
    function key(event: KeyboardEvent) {
      if (event.key === "Escape") setMobileOpen(false);
      if (event.key === "Tab") {
        const elements = Array.from(
          sidebarRef.current?.querySelectorAll<HTMLElement>("a[href],button") ||
            [],
        ).filter((e) => e.offsetParent !== null);
        if (!elements.length) return;
        const first = elements[0],
          last = elements[elements.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        }
        if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [mobileOpen]);
  const current =
    navigation.find((n) => n.path === location.pathname)?.label ||
    "Analysis report";
  return (
    <div className={`app-shell ${collapsed ? "is-collapsed" : ""}`}>
      <a href="#main-content" className="skip-link">
        Skip to workspace
      </a>
      {mobileOpen && (
        <button
          className="mobile-backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <aside
        className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}
        aria-label="Main navigation"
        ref={sidebarRef}
        role={mobileOpen ? "dialog" : undefined}
        aria-modal={mobileOpen || undefined}
      >
        <Link to="/" className="brand" onClick={() => setMobileOpen(false)}>
          <span className="brand-mark">
            D<span />
          </span>
          <span className="brand-text">
            DELPHI<small>Predictive Intelligence</small>
          </span>
        </Link>
        <button
          className="icon-button mobile-close"
          onClick={() => setMobileOpen(false)}
          aria-label="Close navigation"
        >
          <X size={18} />
        </button>
        <nav>
          {["Workspace", "Intelligence", "Operations"].map((group) => (
            <div className="nav-group" key={group}>
              <div className="nav-group-label">{group}</div>
              {navigation
                .filter((n) => n.group === group)
                .map(({ path, label, icon: Icon }) => (
                  <NavLink
                    key={path}
                    to={path}
                    end
                    title={collapsed ? label : undefined}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      `nav-item ${isActive ? "active" : ""}`
                    }
                  >
                    <Icon size={17} strokeWidth={1.6} />
                    <span>{label}</span>
                  </NavLink>
                ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <Link to="/status" className="sidebar-health">
            <Status
              value={healthError ? "Disconnected" : systemStatus?.status}
            />
            <small>
              {systemStatus
                ? `API ${systemStatus.api_version}`
                : "API status unavailable"}
            </small>
          </Link>
          <button
            className="icon-button collapse-button"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? (
              <ChevronsRight size={16} />
            ) : (
              <ChevronsLeft size={16} />
            )}
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <button
            className="icon-button mobile-menu"
            aria-label="Open navigation"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{current}</strong>
          </div>
          <form
            className="global-search"
            onSubmit={(e) => {
              e.preventDefault();
              navigate(`/search?q=${encodeURIComponent(search)}`);
            }}
          >
            <Search size={15} />
            <input
              id="global-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search workspace…"
              aria-label="Global search"
            />
            <kbd>
              <Command size={10} /> K
            </kbd>
          </form>
          <SystemClock />
          <Link
            to="/status"
            className={`connection-dot ${healthError ? "negative" : systemStatus?.status === "ok" ? "positive" : ""}`}
            aria-label={
              healthError ? "API disconnected" : "API connection status"
            }
            title={healthError || systemStatus?.status || "Checking connection"}
          />
          <div className="topbar-divider" />
          <button
            className="icon-button"
            aria-label="Notifications"
            onClick={() => setDialog("notifications")}
          >
            <Bell size={17} />
          </button>
          <button
            className="application-menu"
            aria-label="Application menu"
            onClick={() => setDialog("application")}
          >
            D
          </button>
        </header>
        <main id="main-content" tabIndex={-1} key={location.pathname}>
          <div className="workspace">{children}</div>
          <footer className="workspace-footer">
            <span>DELPHI / Intelligence workspace</span>
            <span>Browser session</span>
          </footer>
        </main>
      </div>
      {dialog && (
        <Drawer
          title={
            dialog === "notifications"
              ? "Workspace notifications"
              : "DELPHI application"
          }
          onClose={closeDialog}
        >
          {dialog === "notifications" ? (
            <>
              <p className="muted">
                Notifications reflect operations in this session.
              </p>
              {healthError && <p className="notice warning">{healthError}</p>}
              {history.length ? (
                history.map((h, i) => (
                  <div className="activity-row" key={i}>
                    <span>Analysis response received</span>
                    <time>{new Date(h.receivedAt).toLocaleString()}</time>
                  </div>
                ))
              ) : (
                <p className="notice">No analysis notifications yet.</p>
              )}
            </>
          ) : (
            <>
              <p className="muted">
                Application workspace. No account authentication is configured
                in this frontend.
              </p>
              <Metadata
                data={{
                  api_version: systemStatus?.api_version,
                  execution_mode: systemStatus?.execution_mode,
                }}
              />
              <Link
                className="button secondary"
                to="/settings"
                onClick={() => setDialog(null)}
              >
                View configuration
                <ArrowUpRight size={14} />
              </Link>
            </>
          )}
        </Drawer>
      )}
    </div>
  );
}

function SystemClock() {
  const [clock, setClock] = useState(() => new Date());
  useEffect(() => {
    const id = window.setInterval(() => setClock(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);
  return (
    <time className="system-clock" dateTime={clock.toISOString()}>
      {clock.toLocaleTimeString("en-GB", { timeZone: "UTC" })}
      <span>UTC</span>
    </time>
  );
}
