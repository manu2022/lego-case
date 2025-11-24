# Image Question Answering Frontend

Simple React + TypeScript app for uploading images and asking questions about them.

## Project Structure

```
src/
├── components/          # React components
│   ├── ChatArea.tsx    # Message display area
│   ├── InputArea.tsx   # Input form with image upload
│   └── index.ts        # Component exports
├── hooks/              # Custom React hooks
│   └── useImageQuestion.ts  # Image Q&A logic
├── types/              # TypeScript type definitions
│   └── index.ts
├── config.ts           # API configuration
├── App.tsx             # Main app component
├── App.css             # Styles
└── main.tsx            # Entry point
```

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Opens at http://localhost:5173

## Configuration

Edit `src/config.ts` to change the API URL:

```typescript
export const API_URL = 'http://localhost:8000'
```

## Build

```bash
npm run build
```

Output in `dist/` folder

## Docker

Build and run with Docker:

```bash
docker build -t question-answer-frontend .
docker run -p 80:80 question-answer-frontend
```

## Deployment

Deploy to Azure App Service using the deploy script:

```bash
./deploy.sh
```

The script will:
- Auto-increment the version number (stored in `version.txt`)
- Build and push the Docker image to Azure Container Registry
- Update the Azure Web App with the latest image
- Perform a health check

**Prerequisites:**
- Azure CLI installed and logged in
- Terraform infrastructure deployed
- Permissions to access the Container Registry and App Service

## Features

- 📁 Upload images
- ❓ Ask questions about images
- 💬 Get AI-powered answers
- 📊 View token usage
- 🎨 Clean, minimalistic UI
