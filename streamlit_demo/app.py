import streamlit as st
import requests
import json
import pandas as pd

# Constants
DEFAULT_API_ENDPOINT = "http://localhost:8000/api/query"  # Default value

# Page config
st.set_page_config(
    page_title="SIFT Database Query Demo",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 SIFT Database Query Demo")
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
