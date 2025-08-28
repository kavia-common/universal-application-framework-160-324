import React, { useState } from "react";

/**
 * Scheduler allows configuring auto start/stop windows by day.
 * Placeholder state only; ready for API integration.
 */
// PUBLIC_INTERFACE
export default function Scheduler() {
  const [schedule, setSchedule] = useState(defaultSchedule());

  const handleToggleDay = (day) => {
    setSchedule((prev) => ({
      ...prev,
      [day]: { ...prev[day], enabled: !prev[day].enabled }
    }));
  };

  const handleTimeChange = (day, field, value) => {
    setSchedule((prev) => ({
      ...prev,
      [day]: { ...prev[day], [field]: value }
    }));
  };

  const handleSave = () => {
    // Placeholder: POST to backend endpoint when available
    // fetch('/api/scheduler', { method: 'POST', body: JSON.stringify(schedule) })
    console.log("Saving schedule: ", schedule);
    alert("Schedule saved (demo). Check console for payload.");
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Auto Start/Stop Scheduler</h2>
          <button
            onClick={handleSave}
            className="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700"
          >
            Save Schedule
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Define working windows to automatically start and stop non-critical resources. Times are in local timezone.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg divide-y">
        {daysOfWeek.map((d) => (
          <div key={d.key} className="p-4 flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="w-40 flex items-center gap-2">
              <input
                id={`enable-${d.key}`}
                type="checkbox"
                checked={schedule[d.key].enabled}
                onChange={() => handleToggleDay(d.key)}
                className="h-4 w-4"
              />
              <label htmlFor={`enable-${d.key}`} className="text-sm font-medium text-gray-800">
                {d.label}
              </label>
            </div>
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <TimeInput
                label="Start Time"
                value={schedule[d.key].start}
                onChange={(v) => handleTimeChange(d.key, "start", v)}
                disabled={!schedule[d.key].enabled}
              />
              <TimeInput
                label="Stop Time"
                value={schedule[d.key].stop}
                onChange={(v) => handleTimeChange(d.key, "stop", v)}
                disabled={!schedule[d.key].enabled}
              />
              <Select
                label="Policy"
                value={schedule[d.key].policy}
                onChange={(v) => handleTimeChange(d.key, "policy", v)}
                options={[
                  { value: "stop", label: "Stop outside window" },
                  { value: "hibernate", label: "Hibernate outside window" },
                ]}
                disabled={!schedule[d.key].enabled}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-md p-4 text-sm">
        Tip: Pair schedules with AI recommendations for best savings. You can preview suggested shutdown hours on the Reports page.
      </div>
    </div>
  );
}

function defaultSchedule() {
  const base = { enabled: true, start: "09:00", stop: "18:00", policy: "stop" };
  return daysOfWeek.reduce((acc, d) => ({ ...acc, [d.key]: { ...base } }), {});
}

const daysOfWeek = [
  { key: "mon", label: "Monday" },
  { key: "tue", label: "Tuesday" },
  { key: "wed", label: "Wednesday" },
  { key: "thu", label: "Thursday" },
  { key: "fri", label: "Friday" },
  { key: "sat", label: "Saturday" },
  { key: "sun", label: "Sunday" },
];

function TimeInput({ label, value, onChange, disabled }) {
  return (
    <div className="flex flex-col">
      <label className="text-xs text-gray-600 mb-1">{label}</label>
      <input
        type="time"
        className="border rounded-md px-3 py-2 text-sm disabled:bg-gray-100"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />
    </div>
  );
}

function Select({ label, value, onChange, options, disabled }) {
  return (
    <div className="flex flex-col">
      <label className="text-xs text-gray-600 mb-1">{label}</label>
      <select
        className="border rounded-md px-3 py-2 text-sm disabled:bg-gray-100"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}
