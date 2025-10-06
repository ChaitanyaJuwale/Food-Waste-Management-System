import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -------------------------------
# Database connection (PostgreSQL)
# -------------------------------
DB_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/foodwaste"
engine = create_engine(DB_URL)

# -------------------------------
# Query helper
# -------------------------------
def run_query(sql, params=None):
    return pd.read_sql(sql, con=engine, params=params)

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")
st.title("🥗 Local Food Wastage Management Dashboard")

# Sidebar
menu = st.sidebar.radio("Navigate", ["Overview", "Providers", "Receivers", "Food Listings", "Claims", "Analytics", "Query"])

# -------------------------------
# Overview
# -------------------------------
if menu == "Overview":
    col1, col2, col3, col4 = st.columns(4)

    providers = run_query("SELECT COUNT(*) FROM providers;").iloc[0, 0]
    receivers = run_query("SELECT COUNT(*) FROM receivers;").iloc[0, 0]
    listings = run_query("SELECT COUNT(*) FROM food_listings;").iloc[0, 0]
    claims = run_query("SELECT COUNT(*) FROM claims;").iloc[0, 0]

    col1.metric("Providers", providers)
    col2.metric("Receivers", receivers)
    col3.metric("Food Listings", listings)
    col4.metric("Claims", claims)

# -------------------------------
# Providers
# -------------------------------
elif menu == "Providers":
    st.subheader("Providers")
    df = run_query("SELECT * FROM providers;")
    st.dataframe(df)

    fig = px.bar(df.groupby("city").size().reset_index(name="count"), x="city", y="count", title="Providers by City")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Receivers
# -------------------------------
elif menu == "Receivers":
    st.subheader("Receivers")
    df = run_query("SELECT * FROM receivers;")
    st.dataframe(df)

    fig = px.bar(df.groupby("city").size().reset_index(name="count"), x="city", y="count", title="Receivers by City")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Food Listings
# -------------------------------
elif menu == "Food Listings":
    st.subheader("Food Listings")
    df = run_query("SELECT * FROM food_listings;")
    st.dataframe(df)

    # User selects reference date
    reference_date = st.date_input("Select reference date", pd.to_datetime("2025-03-15"))

    # Convert to string for query
    ref_date_str = reference_date.strftime("%Y-%m-%d")

    query = f"""
    SELECT food_id, food_name, expiry_date, location, quantity
    FROM food_listings
    WHERE expiry_date BETWEEN '{ref_date_str}' AND '{ref_date_str}'::DATE + INTERVAL '1 day'
    ORDER BY expiry_date;
    """

    # Run query
    try:
        df = pd.read_sql(query, con=engine)
        if not df.empty:
            st.dataframe(df)

            # Optional: Highlight soon-to-expire
            st.write(f"**Total Near-Expiry Items:** {len(df)}")
        else:
            st.warning("No near-expiry items for the selected date.")
    except Exception as e:
        st.error(f"Error: {e}")


# -------------------------------
# Claims
# -------------------------------
elif menu == "Claims":
    st.subheader("Claims")
    df = run_query("SELECT * FROM claims;")
    st.dataframe(df)

    fig = px.bar(df.groupby("status").size().reset_index(name="count"), x="status", y="count", title="Claims")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Analytics
# -------------------------------
elif menu == "Analytics":
    st.subheader("Analytics")

    # Top provider types by quantity posted
    df = run_query("""
        SELECT p.type, SUM(f.quantity) AS total_quantity
        FROM providers p
        JOIN food_listings f ON p.provider_id = f.provider_id
        GROUP BY p.type
        ORDER BY total_quantity DESC;
    """)
    fig = px.pie(df, values="total_quantity", names="type", title="Quantity Posted by Provider Type")
    st.plotly_chart(fig, use_container_width=True)

    # Most common food types
    df2 = run_query("""
        SELECT food_type, COUNT(*) AS count
        FROM food_listings
        GROUP BY food_type
        ORDER BY count DESC;
    """)
    fig2 = px.bar(df2, x="food_type", y="count", title="Most Common Food Types")
    st.plotly_chart(fig2, use_container_width=True)


# -------------------------------
# Query
# -------------------------------
elif menu == "Query":
    st.title("SQL Query Executor")
    st.write("Enter your SQL query below:")

    user_query = st.text_area("SQL Query", height=200)

    # Initialize session state for query result
    if "query_result" not in st.session_state:
        st.session_state.query_result = None

    if st.button("Run Query"):
        if user_query.strip():
            try:
                df = pd.read_sql(user_query, con=engine)
                st.session_state.query_result = df  # Save to session state
                st.success("Query executed successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a query.")

    # Display last query result if available
    if st.session_state.query_result is not None:
        df = st.session_state.query_result
        st.subheader("Query Result")
        st.dataframe(df)

        # Visualization options
        if not df.empty:
            st.subheader("Visualize Data")

            chart_type = st.selectbox("Select chart type", 
                ["Select", "Table", "Bar", "Line", "Area", "Pie", "Donut", "Combo (Bar + Line)", "Clustered Bar", "Dual Axis", "KPI"], 
                index=0
            )
            
            # If user chooses 'Select' or no chart selected yet
            if chart_type == "Select":
                if len(df) == 1:
                    st.info("Only one row returned. Showing KPIs by default.")
                    for col in df.columns:
                        st.metric(label=col, value=df[col].iloc[0])
                else:
                    st.write("Please select a chart type to visualize the result.")
    
            elif chart_type == "KPI":
                if len(df) == 1:
                    st.subheader("KPI")
                    cols = st.columns(len(df.columns))  # Create columns dynamically
                    for i, col in enumerate(df.columns):
                        with cols[i]:
                            st.metric(label=col, value=df[col].iloc[0])
                else:
                    st.warning("KPI cards are best for single-row results.")
            
            elif chart_type == "Table":
                st.dataframe(df)

            else:
                x_axis = st.selectbox("Select X-axis", df.columns)
                y_axis = st.selectbox("Select Y-axis", df.columns)

                if chart_type == "Bar":
                    st.bar_chart(df.set_index(x_axis)[y_axis])

                elif chart_type == "Line":
                    st.line_chart(df.set_index(x_axis)[y_axis])

                elif chart_type == "Area":
                    st.area_chart(df.set_index(x_axis)[y_axis])

                elif chart_type == "Pie":
                    import plotly.express as px
                    fig = px.pie(df, names=x_axis, values=y_axis, title="Pie Chart")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Donut":
                    import plotly.express as px
                    fig = px.pie(df, names=x_axis, values=y_axis, hole=0.4, title="Donut Chart")
                    st.plotly_chart(fig, use_container_width=True)


                elif chart_type == "Combo (Bar + Line)":
                    # For combo chart, need 2 Y-axis columns
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        y_axis2 = st.selectbox("Select second Y-axis", numeric_cols)
                        import altair as alt
                        bar = alt.Chart(df).mark_bar(color='skyblue').encode(
                            x=alt.X(x_axis, sort=None),
                            y=alt.Y(y_axis)
                        )
                        line = alt.Chart(df).mark_line(color='orange').encode(
                            x=alt.X(x_axis, sort=None),
                            y=alt.Y(y_axis2)
                        )
                        combo_chart = (bar + line).properties(width=800, height=400)
                        st.altair_chart(combo_chart, use_container_width=True)
                    else:
                        st.warning("Combo chart requires at least 2 numeric columns.")

                elif chart_type == "Clustered Bar":
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        y_axis2 = st.selectbox("Select second Y-axis", numeric_cols)
                        import plotly.graph_objects as go
                        fig = go.Figure(data=[
                            go.Bar(name=y_axis, x=df[x_axis], y=df[y_axis], marker_color='blue'),
                            go.Bar(name=y_axis2, x=df[x_axis], y=df[y_axis2], marker_color='green')
                        ])
                        fig.update_layout(barmode='group', title="Clustered Bar Chart")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Clustered Bar requires at least 2 numeric columns.")

                elif chart_type == "Dual Axis":
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        y_axis2 = st.selectbox("Select second Y-axis", numeric_cols)
                        import plotly.graph_objects as go
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=df[x_axis], y=df[y_axis], name=y_axis, marker_color='blue'))
                        fig.add_trace(go.Line(x=df[x_axis], y=df[y_axis2], name=y_axis2, line=dict(color='orange')))
                        fig.update_layout(
                            title="Dual Axis Chart",
                            yaxis=dict(title=y_axis),
                            yaxis2=dict(title=y_axis2, overlaying='y', side='right')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Dual Axis chart requires at least 2 numeric columns.")



