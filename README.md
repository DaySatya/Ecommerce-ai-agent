# Ecommerce-ai-agent

An AI-powered solution that answers natural language questions about sales, ads performance, and product metrics by querying a SQL database and generating visualizations.

## ✨ Key Features
- **Natural Language Processing**: Converts questions to SQL queries
- **Multi-Format Responses**: 
  - Raw data (`/query`)
  - Streamed answers (`/query/stream`)
  - Clean summaries (`/query/clean`)
  - Visualizations (`/query/visualize`)
- **Google Gemini Integration**: Uses LLM for query generation
- **Real-time Visualization**: Matplotlib charts for trends

---

## 🛠️ Setup Guide

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Load Data & Initialize DB**
   ```bash
   python load_data.py      # Imports CSV data
   python datab.py          # Sets up tables
   python database.py       # Configures connections
   ```

4. **Add Google API Key**  
   Create `.env` file:
   ```env
   GOOGLE_API_KEY=your_key_here
   ```

5. **Run the Server**
   ```bash
   python main.py
   ```

---

## 🌐 API Endpoints

### 1. Total Sales Analysis
| Endpoint Type | URL |
|--------------|-----|
| Raw Data | [`http://localhost:8000/query?question=What%20is%20my%20total%20sales?`](http://localhost:8000/query?question=What%20is%20my%20total%20sales?) |
| Streamed | [`http://localhost:8000/query/stream?question=What%20is%20my%20total%20sales?`](http://localhost:8000/query/stream?question=What%20is%20my%20total%20sales?) |
| Clean Answer | [`http://localhost:8000/query/clean?question=What%20is%20my%20total%20sales?`](http://localhost:8000/query/clean?question=What%20is%20my%20total%20sales?) |
| Visualization | [`http://localhost:8000/query/visualize?question=Show+me+sales+over+time`](http://localhost:8000/query/visualize?question=Show+me+sales+over+time) |

### 2. RoAS Calculation
| Endpoint Type | URL |
|--------------|-----|
| Raw Data | [`http://localhost:8000/query?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)`](http://localhost:8000/query?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)) |
| Streamed | [`http://localhost:8000/query/stream?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)`](http://localhost:8000/query/stream?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)) |
| Clean Answer | [`http://localhost:8000/query/clean?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)`](http://localhost:8000/query/clean?question=Calculate%20the%20RoAS%20(Return%20on%20Ad%20Spend)) |
| Visualization | [`http://localhost:8000/query/visualize?question=Show+RoAS+trends+by+product`](http://localhost:8000/query/visualize?question=Show+RoAS+trends+by+product) |

### 3. Highest CPC Product
| Endpoint Type | URL |
|--------------|-----|
| Raw Data | [`http://localhost:8000/query?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?`](http://localhost:8000/query?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?) |
| Streamed | [`http://localhost:8000/query/stream?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?`](http://localhost:8000/query/stream?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?) |
| Clean Answer | [`http://localhost:8000/query/clean?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?`](http://localhost:8000/query/clean?question=Which%20product%20had%20the%20highest%20CPC%20(Cost%20Per%20Click)?) |
| Visualization | [`http://localhost:8000/query/visualize?question=Compare+CPC+across+products`](http://localhost:8000/query/visualize?question=Compare+CPC+across+products) |



## 🚀 Quick Test
```bash
# Test total sales analysis
curl "http://localhost:8000/query/clean?question=What%20is%20my%20total%20sales?"

# Open visualization in browser:
xdg-open "http://localhost:8000/query/visualize?question=Show+me+sales+over+time"
```

---
