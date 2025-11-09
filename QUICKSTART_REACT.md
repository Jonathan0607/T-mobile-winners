# Quick Start - React Dashboard

## Installation & Running

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

## What's Included

✅ **Full React Dashboard** with all features:
- Sidebar with T-Mobile logo (auto-loads from `/public/tmobile_logo_black.png`)
- Circular CHI Score indicator
- 24-hour trend line chart
- Action cards with priority colors
- Interactive USA heat map (Present/Predictive toggle)
- Competitive bar chart

✅ **Key Features:**
- Smooth sidebar animations
- Main content expands to full width automatically
- Native CSS transitions
- Better performance
- TypeScript type safety

## Project Structure

```
src/
  ├── components/        # React components
  ├── data/             # Mock data
  ├── App.tsx           # Main app
  └── main.tsx          # Entry point

public/
  └── tmobile_logo_black.png  # Logo (auto-loaded)

package.json            # Dependencies
vite.config.ts         # Vite config
tailwind.config.js     # Tailwind config
tsconfig.json          # TypeScript config
```

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Troubleshooting

**Logo not showing?**
- Make sure `tmobile_logo_black.png` is in the `public/` folder
- The app will fall back to text "🎯 T-Mobile" if logo not found

**Port already in use?**
- Vite will automatically try the next available port
- Check terminal output for the actual port number

**TypeScript errors?**
- Run `npm install` to ensure all types are installed
- Check that `node_modules/@types` contains the required type definitions

## Next Steps

- Customize colors in `tailwind.config.js`
- Add more components in `src/components/`
- Update mock data in `src/data/mockData.ts`
- Add routing with React Router if needed
- Connect to real API endpoints

