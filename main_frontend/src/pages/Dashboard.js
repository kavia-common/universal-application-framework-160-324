import React from "react";

// PUBLIC_INTERFACE
export default function Dashboard() {
  /** Dashboard with savings summary, active services, and alerts (placeholder data) */
  const savingsSummary = {
    month: "August 2025",
    projectedSavings: 1240.57,
    realizedSavings: 982.31,
    percentage: 18.4
  };

  const activeServices = [
    { name: "EC2 (Compute)", count: 12, cost: 420.12, trend: "down" },
    { name: "RDS (Database)", count: 3, cost: 210.55, trend: "flat" },
    { name: "EKS (Kubernetes)", count: 2, cost: 380.90, trend: "up" },
    { name: "S3 (Storage)", count: 48, cost: 120.22, trend: "down" },
  ];

  const alerts = [
    { id: 1, type: "warning", title: "Idle EC2 instances detected", detail: "3 instances idle > 2 hours. Consider auto-stop." },
    { id: 2, type: "info", title: "New recommendation available", detail: "AI suggests weekend shutdown for dev cluster." },
  ];

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-sm text-gray-500">Projected Monthly Savings</div>
          <div className="mt-2 text-3xl font-semibold">${savingsSummary.projectedSavings.toFixed(2)}</div>
          <div className="mt-1 text-xs text-gray-500">{savingsSummary.month}</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500">Realized Savings</div>
          <div className="mt-2 text-3xl font-semibold">${savingsSummary.realizedSavings.toFixed(2)}</div>
          <div className="mt-1 text-xs text-green-700">+{savingsSummary.percentage}% vs baseline</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500">Optimization Status</div>
          <div className="mt-2 flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-green-500 inline-block" />
            <span className="text-sm font-medium text-gray-700">Active</span>
          </div>
          <div className="mt-1 text-xs text-gray-500">Scheduler and AI recommendations enabled</div>
        </Card>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Active Services</h2>
            <span className="text-xs text-gray-500">Placeholder data</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {activeServices.map((s) => (
              <div key={s.name} className="rounded-lg border border-gray-200 p-4 bg-white">
                <div className="text-sm text-gray-500">{s.name}</div>
                <div className="mt-2 text-2xl font-semibold">{s.count}</div>
                <div className="mt-1 text-xs text-gray-500">Monthly Cost: ${s.cost.toFixed(2)}</div>
                <div className="mt-2">
                  <TrendLabel trend={s.trend} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Alerts</h2>
            <span className="text-xs text-gray-500">2 open</span>
          </div>
          <div className="space-y-3">
            {alerts.map((a) => (
              <div key={a.id} className="rounded-md border p-3 flex gap-3 items-start" data-type={a.type}>
                <span className={"mt-0.5 text-xl " + (a.type === "warning" ? "text-yellow-600" : "text-blue-600")}>
                  {a.type === "warning" ? "⚠️" : "ℹ️"}
                </span>
                <div>
                  <div className="font-medium">{a.title}</div>
                  <div className="text-sm text-gray-600">{a.detail}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}

function Card({ children, className = "" }) {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-5 ${className}`}>
      {children}
    </div>
  );
}

function TrendLabel({ trend }) {
  if (trend === "up") return <span className="inline-flex items-center text-xs text-red-700 bg-red-50 border border-red-200 rounded px-2 py-0.5">↑ Cost Up</span>;
  if (trend === "down") return <span className="inline-flex items-center text-xs text-green-700 bg-green-50 border border-green-200 rounded px-2 py-0.5">↓ Cost Down</span>;
  return <span className="inline-flex items-center text-xs text-gray-700 bg-gray-50 border border-gray-200 rounded px-2 py-0.5">→ Stable</span>;
}
