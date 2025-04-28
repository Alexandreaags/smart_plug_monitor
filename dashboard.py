import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import sqlite3
import datetime
import io
import base64


app = dash.Dash(__name__)
server = app.server  # for deployment if needed


# Ajustar a função fetch_data para garantir que sempre busca os dados mais recentes
# Adicionar logs para depuração na função fetch_data
def fetch_data():
    conn = sqlite3.connect(
        "power_data.db", timeout=10
    )  # Adicionar timeout para evitar bloqueios
    df = pd.read_sql_query(
        "SELECT * FROM power_log ORDER BY timestamp ASC", conn
    )  # Garantir ordenação correta
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None:
        # Localiza os timestamps para o fuso "America/Sao_Paulo"
        df["timestamp"] = df["timestamp"].dt.tz_localize("America/Sao_Paulo")

    # Calcular energia acumulada dinamicamente
    df["energy_kwh"] = (df["power_watts"] / 1000.0) * (1 / 3600.0)
    df["energy_kwh"] = df["energy_kwh"].cumsum()

    return df.sort_values("timestamp")


app.layout = html.Div(
    [
        html.H3("Power Monitor Dashboard"),
        html.Div(
            [
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=datetime.datetime.now() - datetime.timedelta(days=7),
                    end_date=datetime.datetime.now(),
                ),
            ],
            style={"margin-bottom": "15px"},
        ),
        dcc.Interval(
            id="interval-component",
            interval=1000,  # Atualizar a cada 1 segundo
            n_intervals=0,
        ),
        html.Div(
            [
                # Power Graph
                html.Div(
                    [
                        html.H4("Power (W)"),
                        dcc.Dropdown(
                            id="agg-power",
                            options=[{"label": "Raw Data", "value": "raw"}],
                            value="raw",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                        dcc.Graph(id="power-graph", config={"displayModeBar": False}),
                        html.Button("Download CSV", id="btn-power"),
                        dcc.Download(id="download-power"),
                    ],
                    className="graph-box",
                ),
                # Energy Graph
                html.Div(
                    [
                        html.H4("Energy (kWh)"),
                        dcc.Dropdown(
                            id="agg-energy",
                            options=[{"label": "Raw Data", "value": "raw"}],
                            value="raw",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                        dcc.Graph(id="energy-graph", config={"displayModeBar": False}),
                        html.Button("Download CSV", id="btn-energy"),
                        dcc.Download(id="download-energy"),
                    ],
                    className="graph-box",
                ),
                # Current Graph
                html.Div(
                    [
                        html.H4("Current (A)"),
                        dcc.Dropdown(
                            id="agg-current",
                            options=[{"label": "Raw Data", "value": "raw"}],
                            value="raw",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                        dcc.Graph(id="current-graph", config={"displayModeBar": False}),
                        html.Button("Download CSV", id="btn-current"),
                        dcc.Download(id="download-current"),
                    ],
                    className="graph-box",
                ),
                # Voltage Graph
                html.Div(
                    [
                        html.H4("Voltage (V)"),
                        dcc.Dropdown(
                            id="agg-voltage",
                            options=[{"label": "Raw Data", "value": "raw"}],
                            value="raw",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                        dcc.Graph(id="voltage-graph", config={"displayModeBar": False}),
                        html.Button("Download CSV", id="btn-voltage"),
                        dcc.Download(id="download-voltage"),
                    ],
                    className="graph-box",
                ),
            ],
            className="chart-container",
        ),
        html.Div(id="interval-log", style={"margin-top": "15px"}),
    ]
)


# === Graph callbacks ===
@app.callback(
    Output("power-graph", "figure"),
    [
        Input("agg-power", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_power_graph(freq, start, end, n_intervals):
    df = fetch_data()
    # Converter os limites de data para datetime com timezone "America/Sao_Paulo"
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["power_watts"],
            mode="lines+markers",
            name="Power (W)",
        )
    )
    fig.update_layout(title="Power over Time", template="plotly_dark")
    return fig


@app.callback(
    Output("energy-graph", "figure"),
    [
        Input("agg-energy", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_energy_graph(freq, start, end, n_intervals):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["energy_kwh"],
            mode="lines+markers",
            name="Energy (kWh)",
        )
    )
    fig.update_layout(title="Energy Consumption", template="plotly_dark")
    return fig


@app.callback(
    Output("current-graph", "figure"),
    [
        Input("agg-current", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_current_graph(freq, start, end, n_intervals):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["current_a"],
            mode="lines+markers",
            name="Current (A)",
        )
    )
    fig.update_layout(title="Current", template="plotly_dark")
    return fig


# Adicionar logs para verificar se o callback está sendo acionado
@app.callback(
    Output("voltage-graph", "figure"),
    [
        Input("agg-voltage", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_voltage_graph(freq, start, end, n_intervals):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["voltage_v"],
            mode="lines+markers",
            name="Voltage (V)",
        )
    )
    fig.update_layout(title="Voltage", template="plotly_dark")
    return fig


# === CSV download callbacks ===
def generate_csv_download(df, filename="data.csv"):
    buffer = io.StringIO()
    df.to_csv(buffer)
    buffer.seek(0)
    return dict(content=buffer.getvalue(), filename=filename)


@app.callback(
    Output("download-power", "data"),
    Input("btn-power", "n_clicks"),
    State("agg-power", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    prevent_initial_call=True,
)
def download_power_csv(n, freq, start, end):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    return generate_csv_download(df[["timestamp", "power_watts"]], "power_data.csv")


@app.callback(
    Output("download-energy", "data"),
    Input("btn-energy", "n_clicks"),
    State("agg-energy", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    prevent_initial_call=True,
)
def download_energy_csv(n, freq, start, end):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    return generate_csv_download(df[["timestamp", "energy_kwh"]], "energy_data.csv")


@app.callback(
    Output("download-current", "data"),
    Input("btn-current", "n_clicks"),
    State("agg-current", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    prevent_initial_call=True,
)
def download_current_csv(n, freq, start, end):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    return generate_csv_download(df[["timestamp", "current_a"]], "current_data.csv")


@app.callback(
    Output("download-voltage", "data"),
    Input("btn-voltage", "n_clicks"),
    State("agg-voltage", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    prevent_initial_call=True,
)
def download_voltage_csv(n, freq, start, end):
    df = fetch_data()
    start_dt = pd.to_datetime(start).tz_localize("America/Sao_Paulo")
    end_dt = (
        pd.to_datetime(end).tz_localize("America/Sao_Paulo")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    return generate_csv_download(df[["timestamp", "voltage_v"]], "voltage_data.csv")


if __name__ == "__main__":
    app.run(debug=True)
