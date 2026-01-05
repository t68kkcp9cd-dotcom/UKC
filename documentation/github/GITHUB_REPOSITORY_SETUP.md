# GitHub Repository Setup Guide

## Repository Structure

### Recommended Repository Layout
```
ultimate-kitchen-compendium/
├── backend/
│   ├── app/
│   ├── docker/
│   ├── requirements/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
├── mobile/
│   ├── ios/
│   └── android/
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
├── scripts/
│   ├── setup.sh
│   ├── backup.sh
│   └── deploy.sh
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE/
├── LICENSE
├── README.md
└── .gitignore
```

## Repository Initialization

### 1. Create GitHub Repository

1. **Go to GitHub.com**
2. **Click "New Repository"**
3. **Repository Settings:**
   - **Repository Name**: ultimate-kitchen-compendium
   - **Description**: Self-hosted kitchen management system
   - **Visibility**: Public (recommended for open source)
   - **Initialize**: Don't add README (we'll add our own)

### 2. Clone Repository Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/ultimate-kitchen-compendium.git
cd ultimate-kitchen-compendium

# Create initial directory structure
mkdir -p {backend,mobile/{ios,android},docs,scripts,.github/{workflows,ISSUE_TEMPLATE,PULL_REQUEST_TEMPLATE}}
```

### 3. Initialize Git Repository

```bash
# Initialize git (if not already initialized)
git init

# Add remote origin
git remote add origin https://github.com/yourusername/ultimate-kitchen-compendium.git

# Create initial commit
git add .
git commit -m "Initial commit: Ultimate Kitchen Compendium"
git push -u origin main
```

## README.md Template

### Main README.md

```markdown
# Ultimate Kitchen Compendium

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

> Your complete, self-hosted kitchen management solution

Take control of your kitchen with Ultimate Kitchen Compendium - the all-in-one solution that helps you reduce waste, save money, and create amazing meals.

## 🌟 Features

### Core Features (Free)
- ✅ **Inventory Management**: Track up to 100 items with expiration alerts
- ✅ **Recipe Storage**: Store up to 50 personal recipes
- ✅ **Meal Planning**: Plan weekly meals with AI assistance
- ✅ **Shopping Lists**: Generate smart shopping lists automatically
- ✅ **Barcode Scanning**: Quick item entry with your camera
- ✅ **Offline Access**: Full functionality without internet
- ✅ **Cross-Platform**: iOS, Android, and web access
- ✅ **Family Sharing**: Multi-user household support

### Premium Features (One-Time Purchase)
- 🚀 **Unlimited Storage**: No limits on inventory and recipes
- 🤖 **AI-Powered**: Smart meal planning and recipe suggestions
- 🛒 **Store Integration**: Price comparison across multiple stores
- 🏠 **Smart Devices**: Connect kitchen scales and appliances
- 🎤 **Voice Cooking**: Step-by-step voice guidance
- 📊 **Advanced Analytics**: Nutrition tracking and insights
- 🌍 **Sustainability**: Waste reduction and carbon tracking

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM, 20GB+ storage
- Linux server (Ubuntu 20.04+ recommended)

### Installation

#### Option 1: Automated Setup (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/ultimate-kitchen-compendium/main/setup-ukc.sh | sudo bash
```

#### Option 2: Docker Compose
```bash
git clone https://github.com/yourusername/ultimate-kitchen-compendium.git
cd ultimate-kitchen-compendium/backend
docker-compose up -d
```

#### Option 3: Development Setup
See [Development Guide](docs/DEVELOPMENT.md)

### Access Your Installation
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

## 📱 Mobile Apps

### iOS
- Download from the App Store
- Search "Ultimate Kitchen Compendium"
- Free download with premium upgrade available

### Android
- Download from Google Play Store
- Search "Ultimate Kitchen Compendium"
- Free download with premium upgrade available

## 📚 Documentation

- [📖 User Guide](docs/USER_GUIDE.md) - Complete user documentation
- [🚀 Quick Start](docs/QUICK_START.md) - Get started in 10 minutes
- [🔧 Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [📊 API Documentation](http://localhost:8000/docs) - Interactive API docs
- [🛠️ Development Guide](docs/DEVELOPMENT.md) - Development setup and guidelines

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with asyncpg
- **Cache**: Redis (optional)
- **AI**: Ollama with local models
- **Auth**: JWT with bcrypt

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI
- **State Management**: React Context + Query
- **Routing**: React Router

### Mobile
- **iOS**: SwiftUI with Core Data
- **Android**: Jetpack Compose with Room
- **Offline Support**: Full offline functionality
- **Cross-Platform**: Consistent experience

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on how to contribute.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for home cooks everywhere
- Thanks to all [contributors](https://github.com/yourusername/ultimate-kitchen-compendium/contributors)
- Special thanks to the open source community

## 📞 Support

- **Documentation**: [docs.ultimatekitchencompendium.com](https://docs.ultimatekitchencompendium.com)
- **Community Discord**: [Join our server](https://discord.gg/ukc)
- **GitHub Issues**: [Report issues](https://github.com/yourusername/ultimate-kitchen-compendium/issues)
- **Email**: support@ultimatekitchencompendium.com

---

**Built with ❤️ for home cooks everywhere. Let's reduce food waste and simplify kitchen management together!** 🍳
```

### Backend README.md

```markdown
# Ultimate Kitchen Compendium - Backend

FastAPI backend for the Ultimate Kitchen Compendium kitchen management system.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- Docker & Docker Compose (recommended)

### Installation

#### Using Docker (Recommended)
```bash
docker-compose up -d
```

#### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements/dev.txt

# Configure environment
cp .env.template .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API endpoints
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── tests/                # Test suite
├── alembic/              # Database migrations
├── requirements/         # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Service orchestration
└── README.md
```

### API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | postgresql+asyncpg://ukc:ukc@localhost:5432/ukc_db |
| `JWT_SECRET_KEY` | JWT signing key | Generate random key |
| `OLLAMA_BASE_URL` | Ollama API endpoint | http://localhost:11434 |
| `LOG_LEVEL` | Logging level | INFO |

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_inventory.py
```

### Development

#### Code Style
- **Black**: Code formatting
- **Flake8**: Linting
- **Mypy**: Type checking

#### Pre-commit Hooks
```bash
# Install pre-commit
pre-commit install

# Run pre-commit
pre-commit run --all-files
```

### Deployment

See [Installation Guide](../docs/INSTALLATION.md) for production deployment instructions.

## 📝 License

MIT License - see [LICENSE](../../LICENSE) for details.
```

### Frontend README.md

```markdown
# Ultimate Kitchen Compendium - Frontend

React/TypeScript frontend for the Ultimate Kitchen Compendium kitchen management system.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── contexts/        # React contexts
│   ├── types/           # TypeScript types
│   ├── hooks/           # Custom hooks
│   └── utils/           # Utilities
├── public/              # Static assets
├── package.json         # Dependencies
└── README.md
```

### Development

#### Available Scripts
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint

#### Environment Variables

Create `.env` file in project root:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_ENVIRONMENT=development
```

### Styling

- **Material-UI**: Component library
- **CSS Modules**: Scoped styling
- **Theme**: Custom theme with brand colors

### Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

### Build

```bash
# Build for production
npm run build

# Serve production build
npx serve -s build
```

## 📝 License

MIT License - see [LICENSE](../../LICENSE) for details.
```

## .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
*.log
logs/

# Database
*.db
*.sqlite3
postgres_data/

# Build artifacts
build/
dist/
*.tar.gz

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React
/build/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build
```

## GitHub Actions CI/CD

### Create `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
          
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements/dev.txt
        
    - name: Lint with flake8
      run: |
        cd backend
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    - name: Test with pytest
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
        
    - name: Build
      run: |
        cd frontend
        npm run build
        
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: frontend-build
        path: frontend/build/

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  docker-build:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Log in to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Build and push Docker images
      run: |
        cd backend
        docker build -t yourusername/ukc-backend:latest .
        docker push yourusername/ukc-backend:latest
```

## Issue Templates

### Create `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. iOS]
 - Browser [e.g. chrome, safari]
 - Version [e.g. 22]

**Additional context**
Add any other context about the problem here.
```

### Create `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Pull Request Template

### Create `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
# Pull Request

## Description

Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context.

Fixes # (issue)

## Type of Change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce.

- [ ] Test A
- [ ] Test B

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

## Branch Protection Rules

### Setting Up Branch Protection

1. **Go to Repository Settings**
2. **Click "Branches" in left sidebar**
3. **Add rule for `main` branch**

#### Branch Protection Settings
- **Require pull request reviews before merging**: ✅
- **Required approving reviews**: 1
- **Dismiss stale PR approvals when new commits are pushed**: ✅
- **Require review from code owners**: ✅
- **Require status checks to pass before merging**: ✅
- **Require branches to be up to date before merging**: ✅
- **Status checks that are required**:
  - `backend-tests`
  - `frontend-tests`
  - `security-scan`
- **Require conversation resolution before merging**: ✅
- **Require signed commits**: ❌ (optional)
- **Require linear history**: ❌ (optional)
- **Include administrators**: ✅

## Repository Settings

### General Settings

#### Features
- **Issues**: ✅ Enable
- **Projects**: ✅ Enable
- **Wiki**: ❌ Disable (use docs folder)
- **Discussions**: ✅ Enable (for community)
- **Sponsorships**: ✅ Enable (if applicable)

#### Pull Requests
- **Allow merge commits**: ✅
- **Allow squash merging**: ✅
- **Allow rebase merging**: ❌
- **Automatically delete head branches**: ✅

### Security Settings

#### Security Policy
Create `SECURITY.md` in repository root:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities to security@ultimatekitchencompendium.com

We will respond within 24 hours and work to resolve the issue promptly.

## Security Practices

- All code changes require review
- Dependencies are regularly updated
- Security scanning is performed on all commits
- User data is encrypted at rest and in transit
```

#### Security Advisories
- Enable security advisories for responsible disclosure

#### Dependabot
- **Enable Dependabot**: ✅
- **Security Updates**: ✅
- **Version Updates**: ✅

### Secrets Management

#### Required Secrets
Add these to GitHub repository settings:

1. **DOCKER_USERNAME**: Your Docker Hub username
2. **DOCKER_PASSWORD**: Your Docker Hub password/token
3. **CODECOV_TOKEN**: Codecov upload token (optional)
4. **SLACK_WEBHOOK**: Slack notification webhook (optional)

## Community Guidelines

### Create `CODE_OF_CONDUCT.md`

```markdown
# Code of Conduct

## Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Our Standards

### Positive Behavior
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Unacceptable Behavior
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at support@ultimatekitchencompendium.com. All complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 1.4, available at https://www.contributor-covenant.org/version/1/4/code-of-conduct.html
```

## Release Process

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

#### Pre-Release
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Security scan passed
- [ ] Performance testing completed

#### Release
- [ ] Create release branch
- [ ] Update version numbers
- [ ] Update changelog
- [ ] Create release notes
- [ ] Tag release
- [ ] Build and deploy

#### Post-Release
- [ ] Monitor for issues
- [ ] Gather user feedback
- [ ] Update documentation
- [ ] Plan next release

### Release Automation

#### Create `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: |
          Changes in this Release
          - First Change
          - Second Change
        draft: false
        prerelease: false
```

## Monitoring and Analytics

### GitHub Insights
- **Traffic**: Monitor repository visits and clones
- **Contributors**: Track contributor activity
- **Issues**: Monitor issue trends and resolution
- **Pull Requests**: Track PR activity and merge rates

### External Tools

#### Code Quality
- **Codecov**: Code coverage reporting
- **SonarCloud**: Code quality analysis
- **LGTM**: Security vulnerability scanning

#### Project Management
- **ZenHub**: Project management integration
- **Snyk**: Security vulnerability monitoring
- **Renovate**: Automated dependency updates

## Backup and Recovery

### Repository Backup

#### Automated Backup
```bash
# Create backup script
cat > backup-repo.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
git clone --mirror https://github.com/yourusername/ultimate-kitchen-compendium.git backup-$DATE.tar
tar -czf backup-$DATE.tar.gz backup-$DATE/
rm -rf backup-$DATE/
EOF

# Schedule backup
crontab -e
# Add: 0 2 * * * /path/to/backup-repo.sh
```

  #### Recovery Process
  ```bash
  # Restore from backup
  git clone backup-20240101_120000.tar.gz restored-repo
  cd restored-repo
  git remote add origin https://github.com/yourusername/ultimate-kitchen-compendium.git
  git push origin --all
  ```

  ### GitHub Enterprise Backup Utilities
  For enterprise users, consider using GitHub Enterprise backup utilities for comprehensive backup and recovery.

  ## Community Management

  ### Discord/Slack Integration

  #### GitHub-Discord Webhook
  1. **Discord Server Settings** → **Integrations** → **Webhooks**
  2. **Copy Webhook URL**
  3. **GitHub Repository Settings** → **Webhooks** → **Add webhook**
  4. **Payload URL**: Discord webhook URL
  5. **Content type**: application/json
  6. **Events**: Push, Pull requests, Issues

  #### Notification Settings
  - **Push events**: Notify on commits to main
  - **Pull requests**: Notify on PR open/close/merge
  - **Issues**: Notify on issue creation and comments
  - **Releases**: Notify on new releases

  ### All Contributors

  #### Add All Contributors Bot
  1. **Install All Contributors bot** from GitHub Marketplace
  2. **Usage**: Comment on issues/PRs with:
     ```
     @all-contributors please add @username for code, docs, tests
     ```

  #### Contribution Types
  - `code` - Code contributions
  - `doc` - Documentation
  - `test` - Test contributions
  - `bug` - Bug reports
  - `ideas` - Ideas and planning
  - `design` - UI/UX design
  - `review` - Code reviews

  ### Stale Issue Management

  #### Create `.github/workflows/stale.yml`
  ```yaml
  name: Mark stale issues and pull requests

  on:
    schedule:
    - cron: "30 1 * * *"

  jobs:
    stale:
      runs-on: ubuntu-latest
      permissions:
        issues: write
        pull-requests: write

      steps:
      - uses: actions/stale@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          stale-issue-message: 'This issue has been automatically marked as stale because it has not had recent activity. It will be closed if no further activity occurs. Thank you for your contributions.'
          stale-pr-message: 'This PR has been automatically marked as stale because it has not had recent activity. It will be closed if no further activity occurs. Thank you for your contributions.'
          stale-issue-label: 'no-issue-activity'
          stale-pr-label: 'no-pr-activity'
          days-before-stale: 30
          days-before-close: 7
          exempt-issue-labels: 'pinned,security,enhancement'
          exempt-pr-labels: 'pinned,security,enhancement'
  ```

  ## Advanced Configuration

  ### GitHub CLI Automation

  #### Install GitHub CLI
  ```bash
  # macOS
  brew install gh
  
  # Ubuntu/Debian
  sudo apt install gh
  
  # Windows (via PowerShell)
  winget install --id GitHub.cli
  ```

  #### Authenticate
  ```bash
  gh auth login
  ```

  #### Repository Management
  ```bash
  # Create repository
  gh repo create yourusername/ultimate-kitchen-compendium --public
  
  # Clone repository
  gh repo clone yourusername/ultimate-kitchen-compendium
  
  # Create issue
  gh issue create --title "Bug: Login not working" --body "Cannot login with valid credentials"
  
  # Create pull request
  gh pr create --title "Add new feature" --body "Description of changes"
  
  # View workflows
  gh workflow view
  ```

  ### Repository Metrics

  #### GitHub API for Metrics
  ```bash
  # Get repository statistics
  gh api repos/yourusername/ultimate-kitchen-compendium/stats/contributors
  
  # Get traffic data
  gh api repos/yourusername/ultimate-kitchen-compendium/traffic/views
  
  # Get clone data
  gh api repos/yourusername/ultimate-kitchen-compendium/traffic/clones
  ```

  #### Custom Dashboard Script
  ```python
  #!/usr/bin/env python3
  import requests
  import json
  from datetime import datetime
  
  # Repository metrics script
  def get_repo_metrics(owner, repo, token):
      headers = {'Authorization': f'token {token}'}
      base_url = f'https://api.github.com/repos/{owner}/{repo}'
      
      # Get basic stats
      repo_info = requests.get(base_url, headers=headers).json()
      
      # Get issues
      issues = requests.get(f'{base_url}/issues?state=all', headers=headers).json()
      
      # Get pull requests
      prs = requests.get(f'{base_url}/pulls?state=all', headers=headers).json()
      
      return {
          'stars': repo_info.get('stargazers_count', 0),
          'forks': repo_info.get('forks_count', 0),
          'open_issues': repo_info.get('open_issues_count', 0),
          'total_issues': len(issues),
          'total_prs': len(prs),
          'last_updated': repo_info.get('updated_at')
      }
  
  if __name__ == '__main__':
      metrics = get_repo_metrics('yourusername', 'ultimate-kitchen-compendium', 'YOUR_TOKEN')
      print(json.dumps(metrics, indent=2))
  ```

  ### Performance Optimization

  #### Repository Size Management
  ```bash
  # Check repository size
  git count-objects -vH
  
  # Remove large files from history
  git filter-branch --tree-filter 'rm -rf large-file.zip' HEAD
  
  # Use Git LFS for large files
  git lfs track "*.zip"
  git lfs track "*.tar.gz"
  git add .gitattributes
  ```

  #### Git LFS Setup
  ```bash
  # Install Git LFS
  git lfs install
  
  # Track large file types
  git lfs track "*.psd"
  git lfs track "*.zip"
  git lfs track "*.tar.gz"
  git lfs track "*.dmg"
  git lfs track "*.exe"
  
  # Commit .gitattributes
  git add .gitattributes
  git commit -m "Add Git LFS tracking"
  ```

  ### Legal and Compliance

  #### License Scanner
  ```bash
  # Install license scanner
  npm install -g license-checker
  
  # Check licenses
  license-checker --summary
  ```

  #### DCO Sign-off
  ```bash
  # Configure DCO sign-off
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  
  # Auto-signoff all commits
  git config --global format.signoff true
  ```

  ---

  ## Summary Checklist

  ### Repository Setup Complete ✅
  - [ ] Repository created on GitHub
  - [ ] Local repository initialized
  - [ ] Directory structure created
  - [ ] README.md files created
  - [ ] .gitignore configured
  - [ ] Initial commit pushed

  ### CI/CD Pipeline ✅
  - [ ] GitHub Actions workflows created
  - [ ] Backend testing configured
  - [ ] Frontend testing configured
  - [ ] Security scanning enabled
  - [ ] Docker build automation setup

  ### Community Management ✅
  - [ ] Issue templates created
  - [ ] Pull request template created
  - [ ] Code of conduct added
  - [ ] Contributing guidelines added
  - [ ] Branch protection rules configured

  ### Security ✅
  - [ ] Security policy created
  - [ ] Dependabot enabled
  - [ ] Secrets configured
  - [ ] Vulnerability scanning active

  ### Documentation ✅
  - [ ] Main README.md complete
  - [ ] Backend README.md complete
  - [ ] Frontend README.md complete
  - [ ] API documentation accessible
  - [ ] Changelog created

  ### Monitoring ✅
  - [ ] Codecov integration
  - [ ] Repository insights enabled
  - [ ] Backup procedures established
  - [ ] Release process documented

  ---

  **Your GitHub repository is now fully configured and ready for development!** 🚀

#### Recovery Process
```bash
# Restore from backup
git clone backup-20240101_120000.tar.gz restored-repo
cd restored-repo
git remote add origin https://github.com/yourusername/ultimate-kitchen-compendium.git
git push --mirror origin
```

---

**This GitHub repository setup provides a solid foundation for managing the Ultimate Kitchen Compendium project with proper CI/CD, security, and community practices.**