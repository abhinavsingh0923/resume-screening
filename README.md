# AI-Powered Resume Screening Application

A modern web application that uses AI to screen and evaluate resumes against job descriptions, providing instant feedback and candidate rankings.

## 🚀 Features

- **Bulk Resume Processing**: Upload and analyze multiple resumes (up to 10) at once
- **Smart Matching**: AI-powered matching of candidate skills and experience to job requirements
- **Detailed Analysis**: Get comprehensive insights for each candidate
- **Visual Results**: View candidate rankings and score distributions through interactive charts
- **PDF Support**: Upload job descriptions and resumes in PDF format

## 📋 Requirements

- Python 3.8+
- Google Gemini API key

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-screening.git
   cd resume-screening
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Follow the on-screen instructions:
   - Enter your Google Gemini API key (if not in .env file)
   - Paste a job description or upload a JD PDF
   - Upload resume PDFs (1-10 files)
   - Click "Screen Resumes"
   - View the results and analysis

## 🧠 How It Works

The application uses a LangGraph workflow to process resumes:

1. **Document Loading**: Extracts text from PDF resumes
2. **Data Extraction**: Parses resume content into structured data
3. **JD Matching**: Compares resume data against job requirements
4. **Scoring**: Evaluates candidates based on multiple criteria
5. **Visualization**: Presents results in an easy-to-understand format

## 🛠️ Development

### Project Structure

- `app.py`: Streamlit frontend application
- `workflow.py`: LangGraph workflow definition
- `chains.py`: LLM chain definitions for resume processing
- `.env`: Environment variables (API keys)

### Running Tests

```bash
pytest
```

### Using the Makefile

The project includes a Makefile with common commands:

```bash
# Run the application
make run

# Run tests
make test

# Format code
make format

# Check code quality
make lint
```

## 📄 License

[MIT License](LICENSE)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.