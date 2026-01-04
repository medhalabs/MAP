# Frontend - MedhaAlgoPilot

Next.js frontend for the algorithmic trading platform.

## Features

- Dashboard with account overview
- Strategy management
- Order and trade audit
- Real-time P&L tracking
- Risk monitoring
- WebSocket-based real-time updates

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Pages

- `/` - Landing page
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard` - Main dashboard
- `/dashboard/strategies` - Strategy list
- `/dashboard/strategies/[id]` - Strategy detail
- `/dashboard/orders` - Orders audit
- `/dashboard/positions` - Current positions
- `/dashboard/risk` - Risk monitor

## Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

