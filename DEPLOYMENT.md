# GitHub Pages Deployment Instructions

## Repository: mtg-quiz-app
## Base Path: /mtg-quiz-app/

## One-time Setup (Manual Deployment)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Build the project:**
   ```bash
   npm run build
   ```

3. **Deploy to GitHub Pages:**
   ```bash
   npm run deploy
   ```

## Automatic Deployment (GitHub Actions)

The GitHub Actions workflow will automatically deploy when you push to main/master branch.

1. **Push your code:**
   ```bash
   git add .
   git commit -m "Setup GitHub Pages deployment"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: "gh-pages" (created by deployment)
   - Folder: "/ (root)"

## Local Testing

Test the production build locally:
```bash
npm run build
npm run preview
```

## Troubleshooting

### If deployment fails:
1. Check GitHub Actions logs in your repository
2. Ensure GitHub Pages is enabled in repository settings
3. Make sure the base path in vite.config.js matches your repo name

### If assets don't load:
1. Verify the base path in vite.config.js
2. Should be: `base: '/mtg-quiz-app/'`
3. Update if your repository name is different

### Manual deployment alternative:
```bash
npm run build
npx gh-pages -d dist
```

## Your app will be available at:
https://YOUR_USERNAME.github.io/mtg-quiz-app/

Replace YOUR_USERNAME with your GitHub username.
