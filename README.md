# T-Mobile Vibe Check Dashboard

We are going to win this hackathon! 🏆

## React Dashboard ⚛️

**Tech Stack:** React, TypeScript, Tailwind CSS, Plotly.js, Vite

**Features:**
- ✅ Dark mode with T-Mobile magenta accents (#E20074)
- ✅ Smooth sidebar animations (slides off-screen when hidden)
- ✅ Circular CHI Score indicator with trend
- ✅ 24-hour trend line chart
- ✅ Action cards with priority indicators (Critical/High)
- ✅ Interactive USA heat map (Present/Predictive views)
- ✅ Competitive bar chart
- ✅ Responsive layout
- ✅ TypeScript type safety

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   Navigate to `http://localhost:5173`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
.
├── src/                    # React source code
│   ├── components/         # React components
│   │   ├── Sidebar.tsx     # Sidebar with logo and navigation
│   │   ├── VibeScoreCard.tsx # Circular progress & trend chart
│   │   ├── ActionCards.tsx  # Priority action cards
│   │   ├── HeatMap.tsx      # USA heat map
│   │   └── CompetitiveChart.tsx # Bar chart
│   ├── data/              # Mock data
│   │   └── mockData.ts    # Data definitions
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
│   └── tmobile_logo_black.png # T-Mobile logo
├── package.json           # Dependencies
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

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

## Documentation

- See [README_REACT.md](./README_REACT.md) for detailed documentation
- See [QUICKSTART_REACT.md](./QUICKSTART_REACT.md) for quick start guide

## License

MIT
