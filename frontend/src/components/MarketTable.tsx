import { ArrowDown, ArrowUp } from "@phosphor-icons/react";

import { formatCents, formatEdge, formatPercent, formatVolume } from "../lib/format";
import type { ScoredMarket } from "../types";


interface MarketTableProps {
  markets: ScoredMarket[];
}


export function MarketTable({ markets }: MarketTableProps) {
  if (markets.length === 0) {
    return (
      <div className="empty-market-state">
        <h3>No open contracts</h3>
        <p>Kalshi did not return an open NYC high-temperature market.</p>
      </div>
    );
  }

  return (
    <div className="market-table-wrap">
      <table className="market-table">
        <thead>
          <tr>
            <th scope="col">Temperature range</th>
            <th scope="col">YES bid</th>
            <th scope="col">YES ask</th>
            <th scope="col">Model</th>
            <th scope="col">Edge</th>
            <th scope="col">Volume</th>
          </tr>
        </thead>
        <tbody>
          {markets.map((market) => {
            const isPositive = market.edge > 0;

            return (
              <tr key={market.ticker}>
                <td>
                  <strong>{market.range_label}</strong>
                  <span>{market.ticker}</span>
                </td>
                <td>{formatCents(market.yes_bid)}</td>
                <td>{formatCents(market.yes_ask)}</td>
                <td>{formatPercent(market.model_probability)}</td>
                <td className={isPositive ? "edge positive" : "edge negative"}>
                  {isPositive ? <ArrowUp size={13} weight="bold" /> : <ArrowDown size={13} weight="bold" />}
                  {formatEdge(market.edge)}
                </td>
                <td>{formatVolume(market.volume)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
