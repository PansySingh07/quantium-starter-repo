# application.py
import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# -------------------------
# 1. Locate a CSV (robust)
# -------------------------
candidates = [
    "formatted_output.csv",
    os.path.join("data", "formatted_output.csv"),
]

csv_path = None
for c in candidates:
    if os.path.exists(c):
        csv_path = c
        break

if csv_path is None:
    raise FileNotFoundError("Could not find formatted_output.csv (or cleaned variant). "
                            "Put it in the repo root or in the data/ folder.")

# -------------------------
# 2. Load + robust cleaning
# -------------------------
df = pd.read_csv(csv_path)

# normalize column names
df.columns = df.columns.str.strip()

# map Sales/Date/Region to lowercase canonical names
col_map = {}
for c in df.columns:
    cl = c.strip().lower()
    if cl == "sales":
        col_map[c] = "sales"
    if cl == "date":
        col_map[c] = "date"
    if cl == "region":
        col_map[c] = "region"
df.rename(columns=col_map, inplace=True)

# clean columns (remove $, commas etc), and convert types
# sales: remove non-numeric except dot and minus
if "sales" in df.columns:
    df["sales"] = df["sales"].astype(str).str.strip()
    df["sales"] = df["sales"].str.replace(r"[^0-9.\-]", "", regex=True)
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

# date
if "date" in df.columns:
    df["date"] = df["date"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# region: lowercase & strip
if "region" in df.columns:
    df["region"] = df["region"].astype(str).str.strip().str.lower()

# drop rows missing essential fields
df = df.dropna(subset=["sales", "date", "region"])

# ensure we have rows
if df.empty:
    raise ValueError(f"No valid rows after cleaning in {csv_path} — check the CSV contents.")

# -------------------------
# 3. Build Dash app
# -------------------------
app = Dash(__name__, title="Soul Foods — Pink Morsel Visualiser")

# radio options
region_values = sorted(df["region"].unique())
radio_options = [{"label": r.capitalize(), "value": r} for r in region_values]
radio_options = [{"label": "All", "value": "all"}] + radio_options

app.layout = html.Div(className="container", children=[
    html.Header([
        html.H1("Soul Foods — Pink Morsel Sales Visualiser", className="title"),
        html.P("Use the radio buttons to filter sales by region.", className="subtitle")
    ], className="header"),

    html.Div(className="controls", children=[
        html.Label("Choose region:", className="controls-label"),
        dcc.RadioItems(
            id="region-radio",
            options=radio_options,
            value="all",
            inputStyle={"margin-right": "6px", "margin-left": "12px"},
            className="radio-group"
        )
    ]),

    html.Div(dcc.Graph(id="sales-line-chart"), className="chart")
])


# -------------------------
# 4. Callback
# -------------------------
@app.callback(
    Output("sales-line-chart", "figure"),
    Input("region-radio", "value")
)
def update_graph(selected_region):
    # filter
    if selected_region and selected_region != "all":
        filtered = df[df["region"] == selected_region]
    else:
        filtered = df.copy()

    filtered = filtered.sort_values("date")

    if filtered.empty:
        fig = px.line(title="No data available for this selection")
        return fig

    fig = px.line(
        filtered,
        x="date",
        y="sales",
        title="Pink Morsel Sales Over Time",
        labels={"sales": "Sales ($)", "date": "Date"}
    )

    # add vertical price-increase line with add_shape (works on all plotly versions)
    ymax = filtered["sales"].max()
    if pd.notnull(ymax) and ymax > 0:
        ytop = ymax * 1.05
    else:
        ytop = filtered["sales"].max() if not filtered["sales"].empty else 1

    fig.add_shape(
        type="line",
        x0="2021-01-15",
        x1="2021-01-15",
        y0=0,
        y1=ytop,
        line=dict(color="red", dash="dash"),
    )
    fig.add_annotation(
        x="2021-01-15",
        y=ytop,
        text="Price Increase (15 Jan 2021)",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    )

    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
    return fig


# -------------------------
# 5. Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
