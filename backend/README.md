# Medical Research Search API Backend

This is the backend service for the Medical Research Search application. It provides a comprehensive API that aggregates and analyzes medical research data from multiple sources including FDA, Clinical Trials, and PubMed.

## Features

- Integration with multiple medical research data sources:
  - FDA API for drug and disease information
  - Clinical Trials API for clinical study data
  - NCBI PubMed API for scientific articles
- LangGraph-based workflow for parallel data fetching and processing
- Advanced text summarization using Groq's Mixtral model
- Rate limiting and caching for optimal performance
- Comprehensive error handling and logging
- CORS support for frontend integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys for:
  - Groq (for text generation)
  - FDA (for drug/disease data)
  - OpenAI (optional, for fallback)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file with your API keys and configuration settings.

## Configuration

The application can be configured through environment variables in the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GROQ_API_KEY`: Your Groq API key
- `FDA_API_KEY`: Your FDA API key
- `DEBUG`: Enable debug mode (True/False)
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `CACHE_ENABLED`: Enable caching (True/False)
- `CACHE_TTL`: Cache time-to-live in seconds
- `RATE_LIMIT_ENABLED`: Enable rate limiting (True/False)
- `RATE_LIMIT_REQUESTS`: Maximum requests per period
- `RATE_LIMIT_PERIOD`: Rate limit period in seconds

## Usage

1. Start the server:
```bash
python src/app.py
```

2. The API will be available at `http://localhost:5000`

## API Endpoints

### POST /api/search
Search for medical research information.

Request body:
```json
{
    "query": "your search query",
    "search_type": "drug"  // or "disease"
}
```

Response:
```json
{
    "fda_data": { ... },
    "clinical_trials_data": { ... },
    "ncbi_data": { ... },
    "summary": "AI-generated summary of the research"
}
```

### GET /health
Health check endpoint.

Response:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Development

### Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── fda_api.py
│   │   ├── clinical_trials_api.py
│   │   └── ncbi_api.py
│   ├── utils/
│   │   └── graph_nodes.py
│   ├── app.py
│   └── config.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses Black for code formatting and Flake8 for linting:

```bash
black src/ tests/
flake8 src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 