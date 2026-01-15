# Argument Decomposer

A system that analyzes ethical dilemmas from four distinct analytical perspectives using specialized AI agents. Each perspective provides structured arguments using the Toulmin method with verifiable sources.

## Features

- **Multi-Perspective Analysis**: Four distinct analytical frameworks (Utilitarian, Deontological, Practical, Stakeholder)
- **Toulmin Method Structure**: Structured arguments with Claim, Grounds, Warrant, Backing, Qualifier, and Rebuttal
- **Verifiable Sources**: Citations with clickable URLs for fact-checking
- **Parallel Processing**: Fast response times with concurrent AI agent execution
- **Clean Minimalist UI**: Greyscale color scheme with red accents

## Getting Started

### Prerequisites

- Python 3.12 or later
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/udirno/argument-decomposer.git
   cd argument-decomposer
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   
   Create a `.env` file in the `backend` directory:
   ```bash
   echo "ANTHROPIC_API_KEY=your_key_here" > .env
   ```

4. **Start the backend:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. **Serve the frontend:**
   
   In a new terminal:
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```

6. **Open in browser:**
   Navigate to `http://localhost:8080`

## Usage

Enter an ethical question and click "Analyze" to receive structured perspectives from all four analytical frameworks.

## Tech Stack

- **Backend**: FastAPI, Anthropic Claude API, Python 3.12+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## License

MIT License

---

Built with precision. Crafted for clarity.
