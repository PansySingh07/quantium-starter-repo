import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# -------------------------
# 1. Load cleaned CSV
# -------------------------
csv_path = "formatted_output.csv"
df = pd.read_csv(csv_path)

# Ensure columns are clean
df.columns = [c.strip() for c in df.columns]
df['region'] = df['region'].astype(str).str.strip().str.lower()
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
df = df.dropna(subset=['Sales','date','region'])

# -------------------------
# 2. Create Dash app
# -------------------------
app = Dash(__name__)

# Dropdown options: All + individual regions
regions_options = [{'label':'All Regions','value':'All'}] + \
                  [{'label':r.capitalize(),'value':r} for r in sorted(df['region'].unique())]

app.layout = html.Div([
    html.H1("Soul Foods Pink Morsel Sales Visualiser", style={'textAlign':'center'}),
    
    html.Label("Select Region:"),
    dcc.Dropdown(
        id='region-dropdown',
        options=regions_options,
        value='All',
        multi=False
    ),
    
    dcc.Graph(id='sales-line-chart')
])

# -------------------------
# 3. Callback for chart
# -------------------------
@app.callback(
    Output('sales-line-chart', 'figure'),
    Input('region-dropdown', 'value')
)
def update_graph(selected_region):
    # Filter by region
    if selected_region and selected_region != 'All':
        filtered_df = df[df['region'] == selected_region.lower()]
    else:
        filtered_df = df.copy()
    
    # Sort by date
    filtered_df = filtered_df.sort_values('date')

    # Handle empty data
    if filtered_df.empty:
        fig = px.line(title="No data available for this region")
    else:
        # Create line chart
        fig = px.line(
            filtered_df,
            x='date',
            y='Sales',
            title='Pink Morsel Sales Over Time',
            labels={'Sales':'Sales ($)','date':'Date'}
        )

        # Add vertical line for price increase using add_shape
        fig.add_shape(
            type="line",
            x0="2021-01-15",
            x1="2021-01-15",
            y0=0,
            y1=filtered_df['Sales'].max()*1.05,
            line=dict(color="red", dash="dash"),
        )

        # Add annotation
        fig.add_annotation(
            x="2021-01-15",
            y=filtered_df['Sales'].max()*1.05,
            text="Price Increase",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40
        )

    return fig

# -------------------------
# 4. Run app
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
