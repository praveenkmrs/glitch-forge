# Glitch Forge Frontend

Modern React application with TypeScript, Vite, and TailwindCSS.

## 🏗️ Architecture

```
src/
├── main.tsx           # Application entry point
├── App.tsx            # Root component
├── index.css          # Global styles (Tailwind)
├── components/        # Reusable UI components
├── pages/             # Page components
├── hooks/             # Custom React hooks
├── services/          # API client and services
├── utils/             # Utility functions
├── types/             # TypeScript type definitions
├── context/           # React Context providers
└── tests/             # Test files
```

## 🎯 Design Decisions

### 1. **Vite over Create React App**
- **10-100x faster** dev server startup
- **Hot Module Replacement (HMR)** is instant
- Modern, actively maintained
- Smaller bundle sizes

### 2. **Mobile-First Approach**
- Base styles for mobile (320px+)
- Progressive enhancement for larger screens
- Touch-friendly interactions
- Optimized for slow networks

### 3. **TailwindCSS**
- Utility-first CSS
- Smaller bundle (unused styles purged)
- Consistent design system
- Faster development

### 4. **TypeScript**
- Type safety prevents bugs
- Better IDE autocomplete
- Self-documenting code
- Easier refactoring

### 5. **State Management**
- **Zustand**: Client state (simple, powerful)
- **React Query**: Server state (caching, sync)
- **React Context**: Auth and global state

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

Visit http://localhost:3000

### With Docker

```bash
# From project root
docker-compose up frontend
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## 📝 Code Quality

```bash
# Type check
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

## 📦 Building for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

## 🎨 Styling Guidelines

### Mobile-First Example

```tsx
// ❌ Desktop-first (wrong)
<div className="text-xl md:text-base">

// ✅ Mobile-first (correct)
<div className="text-base md:text-xl">
```

### Responsive Breakpoints

```tsx
// Mobile: base styles (no prefix)
// Tablet: sm: (640px+)
// Desktop: md: (768px+)
// Large: lg: (1024px+)

<div className="
  grid
  grid-cols-1          // Mobile: 1 column
  sm:grid-cols-2       // Tablet: 2 columns
  lg:grid-cols-3       // Desktop: 3 columns
">
```

### Custom Components

We use `@layer components` for reusable styles:

```tsx
// Use predefined classes
<button className="btn-primary">Click Me</button>
<div className="card">Content</div>
<input className="input" />
```

## 🔒 Security Best Practices

1. **XSS Prevention**: React escapes by default
2. **CSRF**: Include tokens in requests
3. **Secrets**: Never commit `.env` files
4. **Dependencies**: Regular `npm audit`
5. **Content Security Policy**: Configure in nginx

## 📚 Key Libraries

| Library | Purpose | Why? |
|---------|---------|------|
| React 18 | UI library | Concurrent features, modern |
| TypeScript | Type safety | Catch bugs early |
| Vite | Build tool | Fast, modern |
| TailwindCSS | Styling | Utility-first, efficient |
| React Router | Navigation | Standard, powerful |
| Zustand | State mgmt | Simple, no boilerplate |
| React Query | Server state | Caching, sync, retry |
| React Hook Form | Forms | Performance, validation |
| Zod | Validation | TypeScript-first |

## 🐛 Debugging

### In Browser

```tsx
// React DevTools extension
// Inspect component tree and state

// Zustand DevTools
// Monitor store changes

// React Query DevTools
// View cache and network status
```

### VS Code

```json
// .vscode/launch.json
{
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:3000"
}
```

## 📱 Mobile Testing

### Chrome DevTools
- Toggle device toolbar (Cmd+Shift+M)
- Test different screen sizes
- Simulate slow network

### Physical Device Testing
```bash
# Find your local IP
ifconfig | grep "inet "

# Access on mobile using your IP
http://192.168.x.x:3000
```

## 🚢 Deployment

### Production Build
- Static files in `dist/`
- Served by Nginx
- Gzip compression enabled
- Cache headers configured

### Environment Variables
- Prefix with `VITE_` to expose to client
- Never include secrets in frontend code
- Backend should validate all requests
