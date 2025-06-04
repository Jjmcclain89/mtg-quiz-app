#!/usr/bin/env python3
"""
Setup GitHub Pages Deployment

This script configures the MTG Quiz app for GitHub Pages deployment,
including Vite configuration and build setup.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def get_repo_name():
    """Get the repository name for GitHub Pages base path"""
    print("🔍 Detecting repository name...")
    
    try:
        # Try to get from git remote
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True, check=True)
        remote_url = result.stdout.strip()
        
        # Extract repo name from URL
        if 'github.com' in remote_url:
            # Handle both SSH and HTTPS URLs
            if remote_url.endswith('.git'):
                remote_url = remote_url[:-4]
            
            repo_name = remote_url.split('/')[-1]
            print(f"✅ Detected repository: {repo_name}")
            return repo_name
        else:
            print("⚠️  Not a GitHub repository")
            return None
            
    except subprocess.CalledProcessError:
        print("⚠️  Could not detect Git repository")
        return None

def create_vite_config(repo_name):
    """Create or update vite.config.js for GitHub Pages"""
    print("📝 Configuring Vite for GitHub Pages...")
    
    config_path = Path('vite.config.js')
    
    # Determine base path
    if repo_name:
        base_path = f'/{repo_name}/'
    else:
        # Fallback - user will need to update manually
        base_path = '/mtg-quiz-app/'
        print(f"⚠️  Using fallback base path: {base_path}")
        print("   Update this in vite.config.js if your repo name is different")
    
    vite_config = f'''import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [react()],
  base: '{base_path}',
  build: {{
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // Ensure compatibility with GitHub Pages
    rollupOptions: {{
      output: {{
        manualChunks: undefined,
      }}
    }}
  }}
}})
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(vite_config)
    
    print(f"✅ Created vite.config.js with base: '{base_path}'")
    return base_path

def update_package_json():
    """Add deployment scripts to package.json"""
    print("📦 Adding deployment scripts to package.json...")
    
    package_path = Path('package.json')
    
    if not package_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_path, 'r', encoding='utf-8') as f:
        package_data = json.load(f)
    
    # Add deployment scripts
    if 'scripts' not in package_data:
        package_data['scripts'] = {}
    
    package_data['scripts']['build'] = 'vite build'
    package_data['scripts']['preview'] = 'vite preview'
    package_data['scripts']['deploy'] = 'npm run build && npx gh-pages -d dist'
    
    # Add gh-pages as dev dependency
    if 'devDependencies' not in package_data:
        package_data['devDependencies'] = {}
    
    package_data['devDependencies']['gh-pages'] = '^6.0.0'
    
    with open(package_path, 'w', encoding='utf-8') as f:
        json.dump(package_data, f, indent=2)
    
    print("✅ Updated package.json with deployment scripts")
    print("   • Added 'build', 'preview', and 'deploy' scripts")
    print("   • Added gh-pages dev dependency")
    return True

def create_github_workflow():
    """Create GitHub Actions workflow for automatic deployment"""
    print("🔄 Creating GitHub Actions workflow...")
    
    # Create .github/workflows directory
    workflow_dir = Path('.github/workflows')
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Deploy to GitHub Pages

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build
      run: npm run build
      
    - name: Setup Pages
      uses: actions/configure-pages@v4
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: './dist'
        
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
'''
    
    workflow_path = workflow_dir / 'deploy.yml'
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    
    print(f"✅ Created GitHub Actions workflow: {workflow_path}")
    return True

def create_deployment_instructions(repo_name, base_path):
    """Create deployment instructions file"""
    print("📖 Creating deployment instructions...")
    
    instructions = f'''# GitHub Pages Deployment Instructions

## Repository: {repo_name or 'YOUR_REPO_NAME'}
## Base Path: {base_path}

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
2. Should be: `base: '{base_path}'`
3. Update if your repository name is different

### Manual deployment alternative:
```bash
npm run build
npx gh-pages -d dist
```

## Your app will be available at:
https://YOUR_USERNAME.github.io{base_path}

Replace YOUR_USERNAME with your GitHub username.
'''
    
    with open('DEPLOYMENT.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created DEPLOYMENT.md with instructions")

def main():
    print("🚀 Setting up GitHub Pages deployment for MTG Quiz")
    print("=" * 60)
    
    # Verify we're in the correct directory
    if not os.path.exists('package.json'):
        print("❌ Error: package.json not found")
        print("Please run this script from the mtg-quiz-app project root")
        return False
    
    # Get repository name
    repo_name = get_repo_name()
    
    if not repo_name:
        repo_name = input("📝 Enter your GitHub repository name: ").strip()
        if not repo_name:
            print("❌ Repository name is required for GitHub Pages")
            return False
    
    # Setup deployment
    base_path = create_vite_config(repo_name)
    update_package_json()
    create_github_workflow()
    create_deployment_instructions(repo_name, base_path)
    
    print("\n" + "=" * 60)
    print("🎉 GitHub Pages deployment setup complete!")
    print("\n✅ Files created/updated:")
    print("   • vite.config.js - Configured for GitHub Pages")
    print("   • package.json - Added deployment scripts")
    print("   • .github/workflows/deploy.yml - Automatic deployment")
    print("   • DEPLOYMENT.md - Step-by-step instructions")
    
    print("\n🚀 Next steps:")
    print("1. Install gh-pages dependency:")
    print("   npm install")
    print("\n2. Test the build locally:")
    print("   npm run build")
    print("   npm run preview")
    print("\n3. Deploy to GitHub Pages:")
    print("   npm run deploy")
    print("\n4. Or push to GitHub for automatic deployment:")
    print("   git add .")
    print("   git commit -m 'Setup GitHub Pages deployment'")
    print("   git push origin main")
    
    print(f"\n🌐 Your app will be available at:")
    print(f"   https://YOUR_USERNAME.github.io{base_path}")
    print("   (Replace YOUR_USERNAME with your GitHub username)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)