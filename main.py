from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import init_db, get_session
from llm_helper import LLMHelper
from sqlalchemy import text
import io
import matplotlib.pyplot as plt
import pandas as pd
import uvicorn
from typing import Optional
from typing import List, Dict


app = FastAPI(
    title="E-commerce AI Agent API",
    description="API for answering e-commerce data questions",
    version="1.0.0"
)

# Initialize database and LLM (now environment variables are loaded)
engine = init_db()
llm_helper = LLMHelper() # This should now correctly find the GOOGLE_API_KEY

# Schema information for the LLM
SCHEMA_INFO = """
Tables:
1. product_total_sales: date (Date), item_id (String), total_sales (Float), total_units_ordered (Integer)
2. product_ad_sales: date (Date), item_id (String), ad_sales (Float), impressions (Integer), ad_spend (Float), clicks (Integer), units_sold (Integer)
3. product_eligibility: eligibility_datetime_utc (DateTime), item_id (String), eligibility (String), message (String)
"""

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "message": "E-commerce AI Agent API",
        "endpoints": {
            "/query": {
                "description": "Answer data questions",
                "parameters": {
                    "question": "Your natural language question"
                }
            },
            "/query/stream": {
                "description": "Streaming response version",
                "parameters": {
                    "question": "Your natural language question"
                }
            },
            "/query/visualize": {
                "description": "Data visualization endpoint",
                "parameters": {
                    "question": "Question that should return chartable data"
                }
            }
        }
    }

@app.get("/query")
async def answer_question(question: str):
    """Main endpoint for answering questions"""
    try:
        # Generate SQL query
        sql_query = llm_helper.generate_sql_query(question, SCHEMA_INFO)
        if sql_query.startswith("Error"):
            raise HTTPException(status_code=400, detail=sql_query)

        # Execute query
        session = get_session(engine)
        try:
            result = session.execute(text(sql_query))
            rows = [dict(row) for row in result.mappings()]
        finally:
            session.close()

        # Format response
        formatted_response = llm_helper.format_response(question, rows)
        if formatted_response.startswith("Error"):
            raise HTTPException(status_code=400, detail=formatted_response)

        return {
            "question": question,
            "sql_query": sql_query,
            "answer": formatted_response,
            "data": rows
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/query/stream")
async def answer_question_stream(question: str):
    """Streaming version of the query endpoint"""
    def generate():
        try:
            # Generate SQL query
            sql_query = llm_helper.generate_sql_query(question, SCHEMA_INFO)
            if sql_query.startswith("Error"):
                yield f"Error: {sql_query}\n"
                return

            yield f"Generated SQL: {sql_query}\n\n"

            # Execute query
            session = get_session(engine)
            try:
                result = session.execute(text(sql_query))
                rows = [dict(row) for row in result.mappings()]
            finally:
                session.close()

            # Format and stream response
            formatted_response = llm_helper.format_response(question, rows)
            if formatted_response.startswith("Error"):
                yield f"Error: {formatted_response}\n"
                return

            for word in formatted_response.split():
                yield word + " "
                import time
                time.sleep(0.05)  # Simulate typing

        except Exception as e:
            yield f"Error: {str(e)}\n"

    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/query/visualize")
async def visualize_data(question: str, chart_type: Optional[str] = None):
    """Endpoint for data visualization"""
    try:
        # Generate SQL query
        sql_query = llm_helper.generate_sql_query(question, SCHEMA_INFO)
        if sql_query.startswith("Error"):
            raise HTTPException(status_code=400, detail=sql_query)

        # Execute query
        session = get_session(engine)
        try:
            result = session.execute(text(sql_query))
            df = pd.DataFrame([dict(row) for row in result.mappings()])
        finally:
            session.close()

        # Create visualization
        plt.figure(figsize=(10, 6))
        plt.style.use('ggplot')

        # Determine chart type automatically if not specified
        if not chart_type:
            if 'date' in df.columns and len(df) > 3:
                chart_type = 'line'
            elif len(df) <= 10:
                chart_type = 'bar'
            else:
                chart_type = 'histogram'

        # Generate appropriate chart
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            x = 'date'

            if chart_type == 'line':
                for col in df.select_dtypes(include=['number']).columns:
                    if col != 'date':
                        plt.plot(df['date'], df[col], label=col)
                plt.legend()
            elif chart_type == 'bar':
                df.plot(x='date', y=df.select_dtypes(include=['number']).columns[0], kind='bar')
        else:
            x = df.columns[0]
            if chart_type == 'bar':
                df.plot(x=x, y=df.columns[1], kind='bar')
            elif chart_type == 'pie':
                plt.pie(df[df.columns[1]], labels=df[x], autopct='%1.1f%%')

        plt.title(f"Visualization: {question[:50]}...")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()

        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("templates/visualization.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

from fastapi.responses import PlainTextResponse  # Add this import

@app.get("/query/clean", response_class=PlainTextResponse)
async def clean_answer(question: str):
    """Endpoint that returns only the clean answer"""
    try:
        # Generate SQL query
        sql_query = llm_helper.generate_sql_query(question, SCHEMA_INFO)
        if sql_query.startswith("Error"):
            return f"Error: {sql_query}"

        # Execute query
        session = get_session(engine)
        result = session.execute(text(sql_query))
        rows = [dict(row) for row in result.mappings()]
        session.close()

        # Format response
        formatted_response = llm_helper.format_response(question, rows)
        return formatted_response

    except Exception as e:
        return f"Error processing request: {str(e)}"
from fastapi.responses import HTMLResponse

@app.get("/query/html", response_class=HTMLResponse)
async def html_answer(question: str):
    try:
        result = await answer_question(question)  # Reuse your existing endpoint
        return f"""
        <html>
            <head><title>Query Result</title></head>
            <body>
                <h1>{result['question']}</h1>
                <p>{result['answer']}</p>
                <details>
                    <summary>Technical Details</summary>
                    <pre>SQL: {result['sql_query']}</pre>
                    <pre>Data: {result['data']}</pre>
                </details>
            </body>
        </html>
        """
    except Exception as e:
        return f"<html><body>Error: {str(e)}</body></html>"
def run_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )

if __name__ == "__main__":
    run_server()
