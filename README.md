# Medical Research Search Application

A full-stack application that allows users to search across FDA data, clinical trials, and medical news using LangGraph for intelligent data processing.

## Project Structure

```
medical-research-search/
├── backend/           # Flask backend with LangGraph
│   ├── src/          # Source code
│   ├── tests/        # Test files
│   └── requirements.txt
└── frontend/         # React frontend
    ├── src/          # Source code
    ├── public/       # Static files
    └── package.json
```

## Features

- Real-time search across multiple medical data sources
- AI-powered summary generation using LangGraph
- FDA drug and disease information
- Clinical trials data
- Medical news articles
- Modern, responsive UI with Material-UI
- TypeScript for type safety

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

5. Run the development server:
   ```bash
   python src/app.py
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file with:
   ```
   REACT_APP_API_BASE_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Deployment

The application is configured for deployment on Render:

1. Backend:
   - Create a new Web Service
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `gunicorn src.app:app`
   - Add environment variables from `.env`

2. Frontend:
   - Create a new Static Site
   - Set the build command: `npm install && npm run build`
   - Set the publish directory: `build`
   - Add environment variables from `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 