# MarketScout

AI-powered competitive analysis tool using LangChain and Google Gemini API.

## Features

- Automatic competitor research and analysis
- Professional PDF report generation
- Real competitor names and website links
- FastAPI backend with modern web interface

![Alt text](https://i.postimg.cc/T1VTgwBJ/langchain.png)
![Alt text](https://i.postimg.cc/Fz44rv1d/langchain2.png)
![Alt text](https://i.postimg.cc/NfQcZQWZ/langchain3.png)
![Alt text](https://i.postimg.cc/8CfQLc6f/langchain4.png)


## Setup

1. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Configure API key**
   ```bash
   # Create .env file
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

3. **Run application**
   ```bash
   # Linux/Mac
   ./start.sh
   
   # Windows
   start.bat
   
   # Manual
   cd backend && python main.py
   ```

4. **Access web interface**
   ```
   http://localhost:8000
   ```

## Usage

1. Enter business idea and location
2. Click "Start Analysis"
3. Download PDF report with competitor analysis

## API Endpoints

- `POST /api/analyze` - Start analysis
- `GET /api/status/{id}` - Check progress
- `GET /api/download/{id}` - Download PDF

## Requirements

- Python 3.8+
- Google Gemini API key
