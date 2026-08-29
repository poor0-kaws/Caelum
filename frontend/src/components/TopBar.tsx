import { ArrowClockwise, Broadcast, Flask } from "@phosphor-icons/react";

import type { DataMode } from "../types";


interface TopBarProps {
  mode: DataMode;
  isLoading: boolean;
  onModeChange: (mode: DataMode) => void;
  onRefresh: () => void;
}


export function TopBar({
  mode,
  isLoading,
  onModeChange,
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
        <div className="mode-switch" aria-label="Data source">
          <button
            className={mode === "sample" ? "mode-button active" : "mode-button"}
            type="button"
            onClick={() => onModeChange("sample")}
          >
            <Flask size={15} weight="bold" />
            Sample
          </button>
          <button
            className={mode === "live" ? "mode-button active" : "mode-button"}
            type="button"
            onClick={() => onModeChange("live")}
          >
            <Broadcast size={15} weight="bold" />
            Live
          </button>
        </div>

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
