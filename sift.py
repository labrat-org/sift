# Standard library imports
import json

# Third-party imports
from nanodjango import Django
from django.db import connection
from django.http import JsonResponse, HttpResponse
import pandas as pd
import asyncpg

# Constants and configuration
app = Django()


# # A Public Postres SQL database of RNA sequence data and their django admin log data for the site 
# # Some test data in case you don't have your own postgres database
# TEST_DB_STRING = 'postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs'
# TEST_QUERY_STRING = 'select * from django_admin_log limit 1000;'  

# Database functions
async def execute_postgres_query(db_string, query, params=None, limit=10):
    """
    Execute a PostgreSQL query using a single connection
    
    Args:
        db_string (str): PostgreSQL connection string
        query (str): SQL query to execute
        params (dict, optional): Dictionary of query parameters
        limit (int, optional): Maximum number of rows to return. Defaults to 10
    """
    conn = await asyncpg.connect(
        db_string,
        timeout=10.0,  # Connection timeout in seconds
        command_timeout=5.0,  # Query execution timeout in seconds
        server_settings={
            'statement_timeout': '5000'  # Milliseconds
        }
    )
    try:
        async with conn.transaction():
            if params is None:
                cursor = await conn.cursor(query)
            else:
                stmt = await conn.prepare(query)
                if isinstance(params, (list, tuple)):
                    cursor = await stmt.cursor(*params)
                else:
                    cursor = await stmt.cursor(**params)
            
            results = await cursor.fetch(limit)
            return [dict(row) for row in results]
    finally:
        await conn.close()

# Response formatting
async def format_response(df, format_type='json'):
    """
    Format DataFrame response in multiple formats
    Supports: json, csv, html, markdown
    """
    if format_type == 'json':
        return JsonResponse(df.to_dict('records'), safe=False)
        
    elif format_type == 'csv':
        csv_data = df.to_csv(index=False)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="query_results.csv"'
        return response
        
    elif format_type == 'html':
        html_data = df.to_html(index=False)
        return HttpResponse(html_data, content_type='text/html')
        
    elif format_type == 'markdown':
        markdown_data = df.to_markdown(index=False, tablefmt='pipe')
        return HttpResponse(markdown_data, content_type='text/plain')
        
    else:
        return JsonResponse(
            {"error": f"Unsupported format: {format_type}. Use json, csv, html, or markdown"}, 
            status=400
        )

# API endpoints
@app.api.post("/query")
async def async_postgres_query_view(request):
    """Execute a PostgreSQL query and return results in the requested format"""
    data = json.loads(request.body)
    try:
        query = data['query']
        limit = int(data.get('limit', 10))
        params = data.get('params')  # Optional query parameters
        
        results = await execute_postgres_query(
            db_string=data['db_string'],
            query=query,
            params=params,
            limit=limit
        )
        df = pd.DataFrame(results)
        
        format_type = data.get('format', 'json').lower()
        return await format_response(df, format_type)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)