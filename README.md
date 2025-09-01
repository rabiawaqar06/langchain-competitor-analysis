# MarketScout

AI-powered competitive analysis tool that uses LangChain and Google Gemini API to automatically research business competitors and generate professional PDF reports.

## Features

- **AI-Powered Research**: Uses Google Gemini 1.5 Flash model for intelligent competitor analysis
- **Real Competitor Data**: Identifies 5+ named competitors with actual website links
- **Professional Reports**: Generates clean PDF reports with market insights
- **Web Interface**: Modern, responsive UI with real-time progress tracking
- **Fast Analysis**: Complete competitive analysis in under 2 minutes
- **REST API**: Full API access for integration with other tools

## What It Does

Enter any business idea and location (e.g., "coffee shop in Islamabad"), and MarketScout will:
- Research the local market automatically
- Find real competitors with names like "Espresso Lounge F-7" or "Coffee Wagera"
- Analyze their positioning and strategies
- Generate a professional PDF report with actionable insights

![Alt text](https://i.postimg.cc/T1VTgwBJ/langchain.png)
![Alt text](https://i.postimg.cc/Fz44rv1d/langchain2.png)
![Alt text](https://i.postimg.cc/NfQcZQWZ/langchain3.png)
![Alt text](https://i.postimg.cc/8CfQLc6f/langchain4.png)


## Installation

1. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd MarketScout
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Create .env file with your Google Gemini API key
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   # Easy start (recommended)
   ./start.sh        # Linux/Mac
   start.bat         # Windows
   
   # Manual start
   cd backend && python main.py
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

## Usage

### Web Interface
1. Enter your business idea (e.g., "restaurant", "gym", "coffee shop")
2. Specify location (e.g., "Islamabad", "New York", "London")
3. Click "Start Analysis" and watch real-time progress
4. Download the generated PDF report

### Sample Output
For "coffee shop in Islamabad":
- **Named Competitors**: Espresso Lounge F-7, Coffee Wagera, Burning Brownie
- **Website Links**: Direct links to competitor websites for research
- **Market Analysis**: Strategic positioning and recommendations
- **Professional PDF**: Ready-to-use business intelligence report

## API Reference

### Start Analysis
```bash
POST /api/analyze
Content-Type: application/json

{
  "business_idea": "coffee shop",
  "location": "Islamabad"
}
```

### Check Status
```bash
GET /api/status/{analysis_id}
```

### Download Report
```bash
GET /api/download/{analysis_id}
```

## Project Structure

```
MarketScout/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── agent.py             # LangChain competitive analysis agent
│   ├── pdf_generator.py     # PDF report generation
│   └── requirements.txt     # Dependencies
├── frontend/
│   ├── index.html           # Web interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
└── reports/                 # Generated PDF reports
```

## Technical Stack

- **Backend**: FastAPI, LangChain, Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Model**: Google Gemini 1.5 Flash
- **PDF Generation**: ReportLab
- **Environment**: Python 3.8+

## Requirements

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Internet connection for competitor research
