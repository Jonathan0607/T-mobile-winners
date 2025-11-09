# T-Mobile Vibe Check Dashboard - React Version

A modern, responsive dashboard built with React, TypeScript, Tailwind CSS, and Plotly.js.

## Features

- ✅ Dark mode with T-Mobile magenta accents
- ✅ Sidebar with smooth animations (slides off-screen when hidden)
- ✅ Circular progress indicator for CHI Score
- ✅ 24-hour trend line chart
- ✅ Action cards with priority indicators
- ✅ Interactive USA heat map (Present/Predictive views)
- ✅ Competitive bar chart
- ✅ Fully responsive layout

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
  ├── components/          # React components
  │   ├── Sidebar.tsx      # Sidebar with navigation
  │   ├── VibeScoreCard.tsx # Circular progress & trend chart
  │   ├── ActionCards.tsx  # Priority action cards
  │   ├── HeatMap.tsx      # USA heat map
  │   └── CompetitiveChart.tsx # Bar chart
  ├── data/
  │   └── mockData.ts      # Mock data definitions
  ├── App.tsx              # Main app component
  ├── main.tsx             # Entry point
  └── index.css            # Global styles
```

## Key Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS
- **Plotly.js** - Interactive charts
- **react-plotly.js** - React wrapper for Plotly

## Customization

### Colors

Edit `tailwind.config.js` to customize colors:
- `tmobile-magenta`: #E20074
- `critical-red`: #D62828
- `high-yellow`: #FFC300
- `bg-dark`: #1A1A1A
- `bg-card`: #2C2C2C

### Logo

Place your T-Mobile logo in the `public/` folder as:
- `tmobile_logo_black.png` (preferred)
- `tmobile_logo.png` (fallback)

The sidebar will automatically load and display the logo.

## Key Advantages

1. **Better Performance** - Client-side rendering, faster updates
2. **Smoother Animations** - Native CSS transitions
3. **Easier Customization** - Full control over UI/UX
4. **Better Developer Experience** - TypeScript, hot reload, component-based
5. **Professional Quality** - Production-ready code with type safety

## License

MIT
