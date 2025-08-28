# AI Cloud Cost Optimizer - React + Tailwind Frontend

A modern, responsive React dashboard using Tailwind CSS with three main pages:
- Dashboard (savings summary, active services, alerts)
- Scheduler (configure auto start/stop windows)
- Reports (monthly savings chart + AI recommendation preview)

This workspace also contains a FastAPI backend (`../backend`) for AWS EC2 management and AI recommendations (see backend README for setup). This frontend uses placeholder data and is ready for API integration.

## Getting Started

Install and run:

```bash
npm install
npm start
```

Build for production:

```bash
npm run build
```

## Tech

- React 18
- React Router v6
- Tailwind CSS 3 (with PostCSS/Autoprefixer)

## Tailwind

Tailwind is configured via:
- `tailwind.config.js` (content paths include `./src/**/*.{js,jsx}`)
- `postcss.config.js` (plugins: tailwindcss, autoprefixer)
- `src/index.css` uses `@tailwind base; @tailwind components; @tailwind utilities;`

## Structure

- `src/components/Layout.js` — App shell with sidebar and header
- `src/pages/Dashboard.js` — Savings summary, services, alerts
- `src/pages/Scheduler.js` — Day-wise auto start/stop configuration
- `src/pages/Reports.js` — Simple bar chart + hourly recommendation grid

## Integration Notes

- Replace placeholder data with API calls (e.g., fetch from `/ai/recommendation`, `/logs/shutdowns`, etc.)
- Keep environment variables in `.env` (do not hardcode secrets)
- Use `fetch` or your preferred client in pages to wire data

## License

© {current_year} Kavia Labs. All rights reserved.
