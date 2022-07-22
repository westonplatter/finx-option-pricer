import math
from typing import List

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

from finx_option_pricer.option_plot import OptionsPlot
from finx_option_pricer.option_structures import gen_strangle
from dash_apps.utils import calc_max_profit, calc_max_loss, calc_max_loss_strike

###############################################################################
# data prep helpers
def helper_gen_strangle(
    spot_price: float,
    strike_price: float,
    spot_range: List,
    days: int,
    vol_initial: float,
    vol_final: float,
    increment_days=1,
    relative_value=1,
) -> pd.DataFrame:
    "Generate df with the calendar structure"

    option_positions = gen_strangle(
        spot_price=spot_price,
        strike_price=strike_price,
        days=days,
        vol_initial=vol_initial,
        vol_final=vol_final,
    )

    op_plot = OptionsPlot(option_positions=option_positions, strike_interval=5, spot_range=spot_range)

    df = op_plot.gen_value_df_timeincrementing(days, increment_days, value_relative=(relative_value == 1))
    df.set_index("strikes", inplace=True)

    # set time incrementing columns
    columns = [f"t{i*increment_days}" for i, _ in enumerate(df.columns)]
    columns[-1] = "tf"
    df.columns = columns

    return df


###############################################################################
# Dash app

app = dash.Dash()
app.layout = html.Div(
    children=[
        html.H1(children="Strangle"),
        html.Br(),
        html.Br(),
        html.Label("Spot price (S) ---- "),
        dcc.Input(id="id_input_spot_price", value=4100, debounce=True, type="number", min=0),
        html.Br(),
        html.Label("Strike price (K) ---"),
        dcc.Input(id="id_input_strike_price", value=4100, debounce=True, type="number", min=0),
        html.Br(),
        html.Label("Spot range (SR) -- "),
        dcc.Input(id="id_input_spot_range", value=500, debounce=True, type="number", min=0, step=10),
        html.Br(),
        html.Label("Increment Days -- "),
        dcc.Input(id="id_input_increment_days", value=1, debounce=True, type="number", min=1, max=30, step=2),
        html.Br(),
        html.Label("Days ---------"),
        dcc.Input(id="id_input_days", value=20, debounce=True, type="number", min=1, max=60),
        html.Br(),
        html.Label("Vol, initial -- "),
        dcc.Input(id="id_input_vol_initial", value=0.16, debounce=True, type="number", step=0.01),
        html.Br(),
        html.Label("Vol, final --- "),
        dcc.Input(id="id_input_vol_final", value=0.16, debounce=True, type="number", step=0.01),
        html.Br(),
        html.Label("Value Relative --- "),
        dcc.Input(id="id_input_relative_value", value=1, debounce=True, type="number", min=0, max=1, step=1),
        html.Br(),
        html.Label("Vix Percent ------ "),
        dcc.Input(id="id_input_vix_percent", value=0.24, debounce=True, type="number", step=0.01),
        html.Br(),
        html.Label("Vix Std ---------- "),
        dcc.Input(id="id_input_vix_std", value=1.0, debounce=True, type="number", step=0.1),
        html.Br(),
        html.Label("Vix Days -------- "),
        dcc.Input(id="id_input_vix_days", value=10, debounce=True, type="number", step=1),
        html.Br(),
        html.Br(),
        html.Div(id="textarea-output", style={"whiteSpace": "pre-line"}),
        html.Br(),
        dcc.Graph(id="inflow_graph"),
    ]
)


###############################################################################
# UI event callbacks


@app.callback(
    [
        Output("inflow_graph", "figure"),
        Output("textarea-output", "children"),
    ],
    [
        Input("id_input_strike_price", "value"),
        Input("id_input_spot_price", "value"),
        Input("id_input_spot_range", "value"),
        Input("id_input_increment_days", "value"),
        Input("id_input_days", "value"),
        Input("id_input_vol_initial", "value"),
        Input("id_input_vol_final", "value"),
        Input("id_input_relative_value", "value"),
        Input("id_input_vix_percent", "value"),
        Input("id_input_vix_std", "value"),
        Input("id_input_vix_days", "value"),
    ],
)
def update_graph(
    spot_price,
    strike_price,
    spot_range,
    increment_days,
    days,
    vol_initial,
    vol_final,
    relative_value,
    vix_percent,
    vix_std,
    vix_days,
):

    spot_range = [
        spot_price - spot_range,
        spot_price + spot_range,
    ]

    increment_days = int(increment_days)
    assert relative_value in [0, 1], "relative value must be 0 or 1"

    df = helper_gen_strangle(
        spot_price=spot_price,
        strike_price=strike_price,
        spot_range=spot_range,
        vol_initial=vol_initial,
        vol_final=vol_final,
        days=days,
        increment_days=increment_days,
        relative_value=relative_value,
    )

    gdf = df.reset_index().melt(id_vars=["strikes"])
    # gdf looks like this
    # strikes	variable	value
    # 0	3600.0	t0	0.144821
    # 1	3605.0	t0	0.155251

    # time incrementing value of option structure
    fig = px.line(gdf, x="strikes", y="value", color="variable")

    # spot
    fig.add_vline(x=spot_price, line_width=1, line_dash="dash", line_color="black")

    # strike
    fig.add_vline(x=strike_price, line_width=1, line_dash="dash", line_color="red")

    # initial cost
    initial_cost = df.loc[spot_price]["t0"]
    fig.add_hline(y=initial_cost, line_width=1, line_color="orange")

    # metrics
    max_profit = calc_max_profit(df)
    max_loss = calc_max_loss(df)
    

    move_percent = vix_std * vix_percent * math.sqrt(vix_days / 252.0)
    move_underlying = spot_price * move_percent
    upside, downside = spot_price + move_underlying, spot_price - move_underlying
    fig.add_vline(x=upside, line_width=1, line_dash="dash", line_color="green")
    fig.add_vline(x=downside, line_width=1, line_dash="dash", line_color="green")

    max_loss_vix = calc_max_loss_strike(df, downside, upside)

    cost_info = f"""
        initial_cost = {initial_cost:.2f}
        max_profit   =  {max_profit:.2f}
        max_loss     =  {max_loss:.2f}
        max_loss_vix =  {max_loss_vix:.2f}
    """

    return [fig, cost_info]


###############################################################################
# Run app

app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter