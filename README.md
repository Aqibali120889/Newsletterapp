# Newsletter Generator

An AI-powered newsletter generation application built with FastAPI, React, and LangChain. This application allows users to automatically generate professional newsletters by providing topics of interest.

## Features

- AI-powered content generation using HuggingFace models
- Web-based interface built with React and Vite
- Real-time search functionality using DuckDuckGo
- Firebase integration for newsletter storage
- Dark/Light theme support
- Responsive design
- Docker support for easy deployment

## Tech Stack

### Backend
- FastAPI - Modern Python web framework
- LangChain - AI/LLM framework for content generation
- HuggingFace Transformers - AI models
- Firebase Admin SDK - Cloud storage and authentication
- Uvicorn - ASGI server

### Frontend
- React 19
- Vite
- Modern CSS with animations
- Font Awesome icons

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Firebase project (optional, for storage features)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
HUGGINGFACE_MODEL_NAME=distilgpt2  # or your preferred model
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Newsletterapp
```

2. Set up the Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd hosting
npm install
```

## Development

1. Start the backend server:
```bash
./devserver.sh
```
Or manually:
```bash
python main.py
```

2. Start the frontend development server:
```bash
cd hosting
npm run dev
```

## Docker Deployment

Build and run using Docker:

```bash
docker build -t newsletter-app .
docker run -p 8000:8000 newsletter-app
```

## Project Structure

```
├── app/
│   └── routes/           # FastAPI route handlers
├── hosting/             # Frontend React application
│   ├── src/            # React source code
│   └── public/         # Static assets
├── src/
│   └── newsletter generator/  # Core newsletter generation logic
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── devserver.sh      # Development server script
└── Dockerfile        # Container configuration
```

## API Endpoints

- `POST /newsletter/generate` - Generate a newsletter
  - Request body: `{ "topic": "string" }`
  - Response: `{ "topic": "string", "newsletter_content": "string" }`

- `GET /newsletter/status` - Check API status
  - Response: Status of various components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.