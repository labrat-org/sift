import streamlit as st
import requests
import json
import pandas as pd

# Constants
DEFAULT_API_ENDPOINT = "http://localhost:8000/api/query"  # Default value

# Page config
st.set_page_config(
    page_title="🐀 Labrat SIFT Database Query Demo",
    page_icon="🐀",
    layout="wide"
)

# Title and description
st.title("🐀 Labrat SIFT Database Query Demo")
st.markdown("""
This demo allows you to execute PostgreSQL queries through the SIFT microservice.
Enter your database connection string, SQL query, and other parameters below.
""")

# TEST_DB_STRING = 'postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs'
# TEST_QUERY_STRING = 'select * from django_admin_log limit 100;'  

# Input form
with st.form("query_form"):
    # API endpoint configuration
    api_endpoint = st.text_input(
        "API Endpoint",
        value=DEFAULT_API_ENDPOINT,
        help="The SIFT service endpoint URL"
    )
    
    # Database connection
    db_string = st.text_input(
        "Database Connection String",
        value="postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs"
    )
    
    # Query input
    query = st.text_area(
        "SQL Query",
        value="SELECT * FROM django_admin_log LIMIT 100;"
    )
    
    # Additional parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        limit = st.number_input("Result Limit", min_value=1, value=10)
    with col2:
        format_type = st.selectbox(
            "Output Format",
            options=["Table View", "json", "csv", "html", "markdown"],
            index=0  # Makes "Table View" the default
        )
    with col3:
        params = st.text_area(
            "Query Parameters (JSON)",
            placeholder='{"param1": "value1"}',
            help="Optional: Enter parameters as JSON"
        )

    submit_button = st.form_submit_button("Execute Query", type="primary", use_container_width=True)

# Handle form submission
if submit_button:
    if not db_string or not query:
        st.error("Please provide both database connection string and query.")
    else:
        try:
            # Prepare request payload
            payload = {
                "db_string": db_string,
                "query": query,
                "limit": limit,
                "format": "json" if format_type == "Table View" else format_type  # Always send json for Table View
            }
            
            # Add parameters if provided
            if params:
                try:
                    payload["params"] = json.loads(params)
                except json.JSONDecodeError:
                    st.error("Invalid JSON in parameters field")
                    st.stop()

            # Display equivalent API request examples
            st.subheader("Sample API Requests")
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "python-requests",  # Most common Python library
                "python-httplib",    # Standard Python
                "js-async",        # Modern JavaScript
                "js-promises",     # Traditional JavaScript
                "curl",            # CLI tools
                "httpie",          # CLI tools
            ])
            
            # Prepare payloads
            curl_payload = json.dumps(payload).replace('"', '\\"')
            pretty_payload = json.dumps(payload, indent=2)
            
            with tab1:
                st.code(
                    f'import requests\n\n'
                    f'url = "{api_endpoint}"\n'
                    f'headers = {{"Content-Type": "application/json"}}\n'
                    f'payload = {pretty_payload}\n\n'
                    f'response = requests.post(url, json=payload)\n'
                    f'data = response.json()',
                    language="python"
                )

            with tab2:
                st.code(
                    f'import json\n'
                    f'from urllib import request\n\n'
                    f'url = "{api_endpoint}"\n'
                    f'headers = {{"Content-Type": "application/json"}}\n'
                    f'payload = {pretty_payload}\n\n'
                    f'data = json.dumps(payload).encode("utf-8")\n'
                    f'req = request.Request(url, data=data, headers=headers, method="POST")\n'
                    f'with request.urlopen(req) as response:\n'
                    f'    data = json.loads(response.read().decode("utf-8"))',
                    language="python"
                )

            with tab3:
                st.code(
                    f'const url = "{api_endpoint}";\n'
                    f'const payload = {pretty_payload};\n\n'
                    f'async function queryDatabase() {{\n'
                    f'    try {{\n'
                    f'        const response = await fetch(url, {{\n'
                    f'            method: "POST",\n'
                    f'            headers: {{\n'
                    f'                "Content-Type": "application/json"\n'
                    f'            }},\n'
                    f'            body: JSON.stringify(payload)\n'
                    f'        }});\n'
                    f'        const data = await response.json();\n'
                    f'        console.log(data);\n'
                    f'    }} catch (error) {{\n'
                    f'        console.error("Error:", error);\n'
                    f'    }}\n'
                    f'}}\n\n'
                    f'// Call the function\n'
                    f'queryDatabase();',
                    language="javascript"
                )

            with tab4:
                st.code(
                    f'const url = "{api_endpoint}";\n'
                    f'const payload = {pretty_payload};\n\n'
                    f'fetch(url, {{\n'
                    f'    method: "POST",\n'
                    f'    headers: {{\n'
                    f'        "Content-Type": "application/json"\n'
                    f'    }},\n'
                    f'    body: JSON.stringify(payload)\n'
                    f'}})\n'
                    f'    .then(response => response.json())\n'
                    f'    .then(data => console.log(data))\n'
                    f'    .catch(error => console.error("Error:", error));',
                    language="javascript"
                )

            with tab5:
                st.code(
                    f'curl -X POST {api_endpoint} \\\n'
                    f'     -H "Content-Type: application/json" \\\n'
                    f'     -d "{curl_payload}"',
                    language="bash"
                )
            
            with tab6:
                st.code(
                    f'http POST {api_endpoint} \\\n'
                    f'    Content-Type:application/json \\\n'
                    f'    {pretty_payload}',
                    language="bash"
                )

            # Make request to SIFT service
            with st.spinner("Executing query..."):
                response = requests.post(api_endpoint, json=payload)

            # Display results
            if response.status_code == 200:
                st.success("Query executed successfully!")
                
                if format_type == "Table View":
                    data = response.json()
                    st.dataframe(pd.DataFrame(data))
                else:
                    # Show raw output in a code block
                    st.code(response.text, language=format_type)
                
                # Download button for results
                if format_type in ["csv", "json"]:
                    st.download_button(
                        "Download Results",
                        response.text,
                        file_name=f"query_results.{format_type}",
                        mime=f"text/{format_type}"
                    )
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error occurred')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
