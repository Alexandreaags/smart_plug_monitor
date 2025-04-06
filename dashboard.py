import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
import sqlite3

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("IoT Power Monitor"),
    dcc.Graph(id='live-graph'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0)
])

@app.callback(Output('live-graph', 'figure'),
              Input('interval', 'n_intervals'))
def update_graph(n):
    conn = sqlite3.connect("power_data.db")
    df = pd.read_sql_query("SELECT * FROM power_log ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()

    df = df.sort_values("timestamp")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['power_watts'],
                             mode='lines+markers', name='Power (W)'))
    fig.update_layout(xaxis_title='Time', yaxis_title='Power (W)', template='plotly_dark')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
