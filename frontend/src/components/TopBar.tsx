import { ArrowClockwise } from "@phosphor-icons/react";


interface TopBarProps {
  isLoading: boolean;
  onRefresh: () => void;
}


export function TopBar({
  isLoading,
  onRefresh,
}: TopBarProps) {
  return (
    <header className="topbar">
      <div className="brand-block">
        <div className="brand-mark" aria-hidden="true">NY</div>
        <div>
          <p className="brand-name">Weather Market Desk</p>
          <p className="brand-subtitle">New York City high temperature</p>
        </div>
      </div>

      <div className="topbar-actions">
        <button
          className="refresh-button"
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
        >
          <ArrowClockwise size={17} weight="bold" />
          Refresh
        </button>
      </div>
    </header>
  );
}
