export function LoadingDashboard() {
  return (
    <main className="dashboard-shell" aria-label="Loading dashboard">
      <div className="skeleton metric-skeleton" />
      <div className="content-grid">
        <div className="skeleton chart-skeleton" />
        <div className="skeleton recommendation-skeleton" />
      </div>
      <div className="skeleton table-skeleton" />
    </main>
  );
}
