# Advanced Sentiment Analysis with LangChain

This project implements an advanced sentiment analysis system using LangChain and OpenAI's GPT models. It can analyze text sentiment, understand implications, and compare attributes between objects.

## Features

- Sentiment analysis with confidence scores
- Implication detection
- Object comparison and attribute analysis
- Modern web interface with Next.js
- FastAPI backend
- Automated testing and quality checks

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- OpenAI API key
- Git

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd sentiment-analysis
```

2. Set up the Python environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your-api-key-here
```

4. Set up the frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
# From the root directory
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

2. Start the frontend development server:
```bash
# From the frontend directory
npm run dev
```

3. Access the application at `http://localhost:3000`

## Testing and Quality Control

The project includes automated testing and quality checks using GitHub Actions. The workflow:

1. Runs on every push to main and pull requests
2. Performs the following checks:
   - Unit tests with pytest
   - Code coverage reporting
   - Linting with flake8
   - Error count verification (max 5 errors allowed)

### Running Tests Locally

1. Install test dependencies:
```bash
pip install pytest pytest-cov flake8
```

2. Run tests:
```bash
# Run all tests with coverage
pytest --cov=./

# Run linting
flake8 .
```

### Pull Request Process

1. Create a new branch for your changes
2. Make your changes and commit them
3. Push to GitHub and create a pull request
4. The CI workflow will automatically:
   - Run all tests
   - Check code quality
   - Verify error count
   - Generate coverage report
5. The PR can only be merged if:
   - All tests pass
   - Error count is below 5
   - Code coverage meets requirements

## Project Structure

```
sentiment-analysis/
├── backend/
│   └── main.py
├── frontend/
│   ├── pages/
│   └── components/
├── tests/
│   └── test_sentiment_analyzer.py
├── .github/
│   └── workflows/
│       └── test.yml
├── sentiment_analyzer.py
├── requirements.txt
├── setup.cfg
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 