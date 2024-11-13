# sift

A simple async API for querying PostgreSQL databases.

```bash
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT id, name FROM users LIMIT 3"
```

Response:
```json
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]
```

### Getting Started

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Test the API:
   ```bash
   curl -X POST http://localhost:8000/api/query -H "Content-Type: application/json" -d '{"db_string": "your_database_string", "query": "SELECT * FROM your_table"}'
   ```
   Or using HTTPie:
   ```bash
   http POST http://localhost:8000/api/query db_string=your_database_string query="SELECT * FROM your_table"
   ```

### Parameters

The API accepts the following parameters in the POST request body:

| Parameter  | Type    | Required | Description |
|------------|---------|----------|-------------|
| db_string  | string  | Yes      | PostgreSQL connection string (e.g., "postgresql://user:pass@localhost:5432/db") |
| query      | string  | Yes      | SQL query to execute |
| params     | array   | No       | Array of parameters for parameterized queries |
| format     | string  | No       | Response format: "json" (default), "csv", "html", or "markdown" |
| limit      | integer | No       | Maximum number of rows to return (default: 10) |

Example with all parameters:
```bash
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT * FROM products WHERE price > $1 AND category = $2" \
    params:='[50, "Electronics"]' \
    format="csv" \
    limit=100
```

### SQL Query Parameters

The `params` parameter supports multiple formats for parameterized queries:

1. Positional parameters using `$1`, `$2`, etc:
```bash
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT * FROM products WHERE price > $1 AND category = $2" \
    params:='[50, "Electronics"]'
```

2. Named parameters using dictionary:
```bash
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT * FROM products WHERE price > :price AND category = :category" \
    params:='{"price": 50, "category": "Electronics"}'
```

The implementation supports both list/tuple parameters (for positional parameters) and dictionary parameters (for named parameters) through the asyncpg library. Choose the style that makes your queries most readable and maintainable.

Note: When using named parameters, make sure to use the `:paramname` syntax in your query and provide a matching dictionary in the `params` field.

### Response Formats

The API supports multiple output formats using the optional `format` parameter:
- `json` (default)
- `csv`
- `html`
- `markdown`

Example with different formats:

```bash
# JSON format (default)
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT id, name FROM users LIMIT 3" \
    limit=3

[
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"},
    {"id": 3, "name": "Bob Wilson"}
]

# CSV format
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT id, name FROM users LIMIT 3" \
    format=csv \
    limit=3

id,name
1,John Doe
2,Jane Smith
3,Bob Wilson

# HTML format
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT id, name FROM users LIMIT 3" \
    format=html \
    limit=3

<table border="1" class="dataframe">
  <thead>
    <tr><th>id</th><th>name</th></tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>John Doe</td></tr>
    <tr><td>2</td><td>Jane Smith</td></tr>
    <tr><td>3</td><td>Bob Wilson</td></tr>
  </tbody>
</table>

# Markdown format
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT id, name FROM users LIMIT 3" \
    format=markdown \
    limit=3

| id | name       |
|----|------------|
| 1  | John Doe   |
| 2  | Jane Smith |
| 3  | Bob Wilson |

# With query parameters
http POST http://localhost:8000/api/query \
    db_string="postgresql://user:pass@localhost:5432/db" \
    query="SELECT * FROM users WHERE id = $1" \
    params:='[1]' \
    limit=1

[
   {"id": 1, "name": "John Doe"}
   {"id": 2, "name": "Jane Smith"},
   {"id": 3, "name": "Bob Wilson"}
]
```

## Weirdness

We are not using Django models or user authentication in this app. However, Django still generates SQLite and staticfiles content on first run. We've included these in .gitignore as placeholders to avoid the initial setup files being committed.

The SQLite database and staticfiles are only created because Django requires them by default, but they aren't actively used by any of our functionality which focuses on async PostgreSQL queries.
