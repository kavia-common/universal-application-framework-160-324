import React, { useMemo } from "react";

/**
 * Reports shows monthly savings and AI recommendation preview.
 * Uses placeholder data and simple CSS bars (no external chart lib).
 */
// PUBLIC_INTERFACE
export default function Reports() {
  const monthly = useMemo(() => ([
    { month: "Mar", savings: 620 },
    { month: "Apr", savings: 810 },
    { month: "May", savings: 740 },
    { month: "Jun", savings: 920 },
    { month: "Jul", savings: 860 },
    { month: "Aug", savings: 980 },
  ]), []);

  const maxVal = Math.max(...monthly.map(m => m.savings));

  // Placeholder recommendation: list of hours to shutdown (AI backend to integrate)
  const recommendation = {
    user_id: "demo-user",
    instance_id: "i-demo",
    threshold: 0.3,
    shutdown_hours: [0,1,2,3,4,5,6, 120,121,122,123,124,125,126,127] // Mon early, weekend
  };

  return (
    <div className="space-y-6">
      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Monthly Savings</h2>
          <span className="text-xs text-gray-500">Placeholder chart</span>
        </div>
        <div className="mt-6 grid grid-cols-6 gap-4 items-end h-48">
          {monthly.map((m) => {
            const h = Math.round((m.savings / maxVal) * 100);
            return (
              <div key={m.month} className="flex flex-col items-center gap-2">
                <div
                  className="w-10 bg-blue-500 rounded-t"
                  style={{ height: `${h}%` }}
                  title={`$${m.savings}`}
                />
                <div className="text-xs text-gray-600">{m.month}</div>
              </div>
            );
          })}
        </div>
        <div className="mt-3 text-sm text-gray-600">
          Total last 6 months: ${monthly.reduce((a, b) => a + b.savings, 0).toFixed(2)}
        </div>
      </section>

      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">AI Recommendations (Preview)</h2>
          <button
            className="text-sm px-3 py-1.5 rounded-md border border-gray-300 hover:bg-gray-50"
            onClick={() => alert("Would call backend /ai/recommendation in real integration")}
          >
            Refresh
          </button>
        </div>
        <p className="text-sm text-gray-600">
          Preview of recommended shutdown hours based on predicted low usage. Lighter cells indicate hours suggested for shutdown.
        </p>

        <HourGrid shutdownHours={recommendation.shutdown_hours} />
        <div className="mt-3 text-xs text-gray-500">
          User: {recommendation.user_id} · Instance: {recommendation.instance_id} · Threshold: {recommendation.threshold}
        </div>
      </section>
    </div>
  );
}

function HourGrid({ shutdownHours }) {
  // 0..167, Monday start
  const rows = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((label, idx) => ({
    label,
    hours: Array.from({ length: 24 }, (_, h) => idx * 24 + h)
  }));

  return (
    <div className="mt-4 overflow-x-auto">
      <div className="min-w-[720px]">
        <div className="grid grid-cols-[80px_repeat(24,1fr)] gap-1 text-xs">
          <div></div>
          {Array.from({ length: 24 }, (_, h) => (
            <div key={h} className="text-center text-gray-500">{h}</div>
          ))}
          {rows.map((row) => (
            <React.Fragment key={row.label}>
              <div className="text-right pr-2 font-medium text-gray-700">{row.label}</div>
              {row.hours.map((hour) => {
                const isShutdown = shutdownHours.includes(hour);
                return (
                  <div
                    key={hour}
                    className={
                      "h-6 rounded " +
                      (isShutdown ? "bg-red-100 border border-red-200" : "bg-green-100 border border-green-200")
                    }
                    title={`${row.label} ${hour % 24}:00 - ${isShutdown ? "Shutdown" : "Keep Running"}`}
                  />
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
