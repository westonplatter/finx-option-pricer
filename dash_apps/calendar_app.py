import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import math

from dash_apps.utils import calc_max_profit, calc_max_loss, calc_max_loss_strike
from finx_option_pricer.option_structures import gen_calendar
from finx_option_pricer.option_plot import OptionsPlot


###############################################################################
# data prep helpers
def gen_calendar_df(
    spot_price, 
    strike_price, 
    spot_range, 
    days,
    front_vol_initial, 
    front_vol_final, 
    back_vol_initial, 
    back_vol_final,
    front_days: int = 20,
    back_days: int = 21,
    option_type='c', 
    increment_days=1, 
    relative_value=1
):
    """Generate df with the calendar structure"""
    fs = front_vol_initial
    bs = back_vol_initial
    fsf = front_vol_final
    bsf = back_vol_final

    kwargs = dict(
        spot_price=spot_price, 
        strike_price=strike_price,
        front_days=front_days, 
        front_vol=fs,
        front_vol_final=fsf,
        back_days=back_days,
        back_vol=bs,
        back_vol_final=bsf,
        option_type='c',
    )
    # this generates a list of Option Positions
    cal = gen_calendar(**kwargs)

    op_plot = OptionsPlot(
        option_positions=cal,
        strike_interval=5,
        spot_range=spot_range)

    # strikes = [op.option.K for op in op_plot.option_positions]
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
app.layout = html.Div(children = [
    html.H1(children='Calendar'),
    html.Br(),
    html.Br(),

    html.Label("Spot price (S) ---- "),
    dcc.Input(id='id_input_spot_price', value=4100, debounce=True, type='number', min=0),
    html.Br(),

    html.Label("Strike price (K) ---"),
    dcc.Input(id='id_input_strike_price', value=4100, debounce=True, type='number', min=0),
    html.Br(),

    html.Label("Spot range (SR) -- "),
    dcc.Input(id='id_input_spot_range', value=500, debounce=True, type='number', min=0),
    html.Br(),

    html.Label("Increment Days -- "),
    dcc.Input(id='id_input_increment_days', value=1, debounce=True, type='number', min=1, max=30, step=2),
    html.Br(),
    
    html.Label("Front, days ---------"),
    dcc.Input(id='id_input_front_days', value=20, debounce=True, type='number', min=1, max=60),
    html.Br(),

    html.Label("Back, days ---------"),
    dcc.Input(id='id_input_back_days', value=21, debounce=True, type='number', min=1, max=60),
    html.Br(),

    html.Label("Front Vol, initial -- "),
    dcc.Input(id='id_input_front_vol_initial', value=0.16, debounce=True, type='number', step=0.01),
    html.Br(),

    html.Label("Front Vol, final --- "),
    dcc.Input(id='id_input_front_vol_final', value=0.16, debounce=True, type='number', step=0.01),
    html.Br(),

    html.Label("Back Vol, initial -- "),
    dcc.Input(id='id_input_back_vol_initial', value=0.16, debounce=True, type='number', step=0.01),
    html.Br(),

    html.Label("Back Vol, final ---- "),
    dcc.Input(id='id_input_back_vol_final', value=0.16, debounce=True, type='number', step=0.01),
    html.Br(),

    html.Label("Value Relative --- "),
    dcc.Input(id='id_input_relative_value', value=1, debounce=True, type='number', min=0, max=1, step=1),
    html.Br(),

    html.Label("Vix Percent ------ "),
    dcc.Input(id='id_input_vix_percent', value=0.24, debounce=True, type='number', step=0.01),
    html.Br(),

    html.Label("Vix Std ---------- "),
    dcc.Input(id='id_input_vix_std', value=1.0, debounce=True, type='number', step=0.1),
    html.Br(),

    html.Label("Vix Days -------- "),
    dcc.Input(id='id_input_vix_days', value=10, debounce=True, type='number', step=1),
    html.Br(),

    html.Br(),
    html.Div(id='textarea-output', style={'whiteSpace': 'pre-line'}),
    
    dcc.Graph(id='inflow_graph'),
])


###############################################################################
# UI event callbacks

@app.callback(
    [
        Output('inflow_graph', 'figure'),
        Output('textarea-output', 'children'),
        
    ],
    [
        Input('id_input_strike_price', 'value'),
        Input('id_input_spot_price', 'value'),
        Input('id_input_spot_range', 'value'),
        Input('id_input_increment_days', 'value'),
        
        Input('id_input_front_days', 'value'),
        Input('id_input_back_days', 'value'),

        Input('id_input_front_vol_initial', 'value'),
        Input('id_input_front_vol_final', 'value'),
        Input('id_input_back_vol_initial', 'value'),
        Input('id_input_back_vol_final', 'value'),
        Input('id_input_relative_value', 'value'),
        Input('id_input_vix_percent', 'value'),
        Input('id_input_vix_std', 'value'),
        Input('id_input_vix_days', 'value'),
    ]
)
def update_graph(
    spot_price, 
    strike_price,
    spot_range,
    increment_days,
    front_days,
    back_days,
    front_vol_initial, 
    front_vol_final, 
    back_vol_initial, 
    back_vol_final,
    relative_value,
    vix_percent,
    vix_std,
    vix_days,
):

    spot_range = [
        spot_price - spot_range, 
        spot_price + spot_range,
    ]
    
    dte = int(front_days)
    increment_days = int(increment_days)
    assert relative_value in [0, 1], "relative value must be 0 or 1"
        
    df = gen_calendar_df(
        spot_price,
        strike_price,
        spot_range,
        dte,
        front_vol_initial,
        front_vol_final,
        back_vol_initial,
        back_vol_final,
        front_days=front_days,
        back_days=back_days,
        increment_days=increment_days,
        relative_value=relative_value,
        option_type='c'
    )

    gdf = df.reset_index().melt(id_vars=["strikes"])
    # gdf looks like this
    # strikes	variable	value
    # 0	3600.0	t0	0.144821
    # 1	3605.0	t0	0.155251    

    # time incrementing value of option structure
    fig = px.line(gdf, x="strikes", y="value", color='variable')

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

    move_percent = vix_std * vix_percent * math.sqrt(vix_days/252.0)
    move_underlying = spot_price * move_percent
    upside, downside = spot_price + move_underlying, spot_price - move_underlying
    fig.add_vline(x=upside, line_width=1, line_dash="dash", line_color="green")
    fig.add_vline(x=downside, line_width=1, line_dash="dash", line_color="green")

    max_loss_vix = calc_max_loss_strike(df, downside, upside)

    cost_info = f"""
        initial_cost = {initial_cost:.2f}
        max_profit   =  {max_profit:.2f}
        max_loss     = {max_loss:.2f}
        max_loss_vix =  {max_loss_vix:.2f}
    """

    return [fig, cost_info]


###############################################################################
# Run app

app.run_server(debug=True, use_reloader=True, port=9999) # Turn off reloader if inside Jupyter