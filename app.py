# Importing necessary libraries
from datetime import datetime
from dash import html, dcc, dash_table, dash
from dash.dependencies import Input, Output
import pandas as pd
import trades
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# External stylesheets for styling the app
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;700&display=swap',
        'rel': 'stylesheet',
    }
]

# Initializing the Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "TEST VER 1.0 Crypto Arbitrage Scanner"

# Layout of the app
app.layout = html.Div(
    html.Div([
        # Header section with title and description
        html.Div([
            html.H1("Arbitrage Scanner", className='header-title'),
            html.P("Crypto Arbitrage scanner analyzing the top X tokens via coingecko and comparing them on exchanges", className='header-description'),
        ],
        className='header',
        ),
        # Table section to display trades
        html.Div(
            dcc.Loading(
                dash_table.DataTable(
                    id='trades-table',
                    columns=[
                        {'name': 'Coin', 'id': 'symbol'},
                        {'name': '% Difference', 'id': 'profit'},
                        {'name': 'High Exchange (buy)', 'id': 'highExchange'},
                        {'name': 'Low Exchange (sell)', 'id': 'lowExchange'},
                    ],
                    # Styling for the table header and data
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    # Enabling native sorting for the table
                    sort_action='native'
                ),
            ),
        className='table-wrapper'
        ),
        # Div to display the last updated time
        html.Div(id='last-updated-text', className='last-updated'),
        # Attribution text
        html.P("Powered by CoinGecko", className="attribution-text"),
        # Interval component to trigger periodic updates
        dcc.Interval(
            id='interval-component',
            interval=220 * 1000,  # in milliseconds --> MUST stay above 1 minute to prevent rate limiting
            n_intervals=0
        )
    ])
)

from trades import coin_data_global

def display_trades(n):
    # Access the global variable from trades.py
    coin_data = coin_data_global
    # Get possible trades based on the coin data
    possible_trades = trades.get_trades(coin_data)
    # Create a sorted DataFrame based on profit
    df = trades.create_sorted_dataframe(possible_trades, 'profit')
    return df.to_dict('records')

# Callback to update the last updated time text
@app.callback(
    Output(component_id='last-updated-text', component_property='children'),
    Input('interval-component', 'n_intervals')
)
def update_text(n):
    # Get the current time and format it
    current_time = datetime.now()
    current_time_str = current_time.strftime("%m/%d/%Y %H:%M:%S")

    return html.Span('Last updated at {ftime}.'.format(ftime=current_time_str))

# Main entry point for the app
if __name__ == "__main__":
    # Start the asynchronous function (this line should be in trades.py)
    asyncio.run(trades.fetch_data_periodically())
    # Start the Dash app
    app.run_server(debug=False)
