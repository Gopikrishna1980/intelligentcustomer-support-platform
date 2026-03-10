# Intelligent Customer Support Platform - Frontend

Modern Next.js 14 frontend for the AI-powered customer support platform.

## Features

- **Authentication**: Login/Register with JWT token management
- **Real-Time Chat**: WebSocket-based chat with AI bot and agent support
- **Ticket Management**: Create, view, and manage support tickets
- **Analytics Dashboard**: Comprehensive metrics and visualizations
- **Knowledge Base**: Searchable articles with semantic search
- **Dark Mode**: Full dark mode support
- **Responsive Design**: Mobile-first responsive UI

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: Axios + React Query
- **Real-Time**: Socket.io Client
- **Charts**: Recharts
- **Markdown**: React Markdown
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Update .env with your backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open browser
http://localhost:3000
```

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/              # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/           # Dashboard pages
│   │   ├── chat/           # Real-time chat
│   │   ├── tickets/        # Ticket management
│   │   ├── analytics/      # Analytics dashboard
│   │   ├── kb/             # Knowledge base
│   │   └── settings/       # User settings
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   └── providers.tsx       # Global providers
├── components/
│   └── layout/             # Layout components
│       ├── Sidebar.tsx
│       └── Header.tsx
├── hooks/
│   └── useAuth.ts          # Auth hook
├── lib/
│   ├── api.ts              # API client
│   ├── socket.ts           # WebSocket client
│   └── utils.ts            # Utility functions
├── store/
│   └── authStore.ts        # Auth state
├── middleware.ts           # Route protection
├── next.config.js          # Next.js config
├── tailwind.config.ts      # Tailwind config
└── tsconfig.json           # TypeScript config
```

## Key Features Implementation

### Authentication
- JWT token storage in localStorage
- Automatic token refresh
- Protected routes with middleware
- Login/Register forms with validation

### Real-Time Chat
- WebSocket connection with Socket.io
- Message sending and receiving
- Typing indicators
- AI bot auto-response
- Agent takeover support
- Satisfaction rating

### Ticket Management
- Create tickets with AI categorization
- List tickets with filters
- View ticket details with timeline
- Add messages to tickets
- Sentiment analysis display

### Analytics Dashboard
- Key metrics cards
- Ticket trends line chart
- Category distribution pie chart
- Agent performance tracking
- Real-time data refresh

### Knowledge Base
- Article listing with categories
- Semantic search
- Article viewer with markdown
- Vote helpful/not helpful
- View count tracking

## API Integration

All API calls use the centralized API client (`lib/api.ts`):

```typescript
import { authApi, ticketsApi, chatApi, kbApi, analyticsApi } from '@/lib/api'

// Example: Login
const response = await authApi.login('email@example.com', 'password')

// Example: Create ticket
const ticket = await ticketsApi.create({ title, description, priority })
```

## WebSocket Usage

Real-time chat uses Socket.io:

```typescript
import { connectChatWebSocket } from '@/lib/socket'

const socket = connectChatWebSocket(sessionId, token)

socket.on('message', (data) => {
  console.log('New message:', data)
})
```

## Styling

Uses Tailwind CSS with dark mode support:

```tsx
// Light and dark mode classes
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance

- Code splitting with Next.js App Router
- Image optimization with next/image
- Lazy loading components
- React Query for data caching
- WebSocket for efficient real-time updates

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Docker

```bash
# Build image
docker build -t support-frontend .

# Run container
docker run -p 3000:3000 support-frontend
```

## Contributing

1. Create feature branch
2. Make changes
3. Run linter: `npm run lint`
4. Submit pull request

## License

MIT License - see LICENSE file for details
