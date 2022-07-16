import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

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
        front_days=days, 
        front_vol=fs,
        front_vol_final=fsf,
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
    html.H1(children='Calendar Pricer'),
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
    dcc.Input(id='id_input_increment_days', value=1, debounce=True, type='number', min=1, max=30, step=1),
    html.Br(),
    
    html.Label("DTE, days ---------"),
    dcc.Input(id='id_input_dte', value=20, debounce=True, type='number', min=1, max=60, step=1),
    html.Br(),


    html.Label("Front Vol, initial -- "),
    dcc.Input(id='id_input_front_vol_initial', value=0.16, debounce=True, type='number'),
    html.Br(),

    html.Label("Front Vol, final --- "),
    dcc.Input(id='id_input_front_vol_final', value=0.16, debounce=True, type='number'),
    html.Br(),

    html.Label("Back Vol, initial -- "),
    dcc.Input(id='id_input_back_vol_initial', value=0.16, debounce=True, type='number'),
    html.Br(),

    html.Label("Back Vol, final ---- "),
    dcc.Input(id='id_input_back_vol_final', value=0.16, debounce=True, type='number'),
    html.Br(),

    html.Label("Value Relative --- "),
    dcc.Input(id='id_input_relative_value', value=1, debounce=True, type='number', min=0, max=1, step=1),
    html.Br(),

    
    dcc.Graph(id='inflow_graph')
])


###############################################################################
# UI event callbacks

@app.callback(
    Output('inflow_graph', 'figure'),
    Input('id_input_strike_price', 'value'),
    Input('id_input_spot_price', 'value'),
    Input('id_input_spot_range', 'value'),
    Input('id_input_increment_days', 'value'),
    Input('id_input_dte', 'value'),
    Input('id_input_front_vol_initial', 'value'),
    Input('id_input_front_vol_final', 'value'),
    Input('id_input_back_vol_initial', 'value'),
    Input('id_input_back_vol_final', 'value'),
    Input('id_input_relative_value', 'value'),
)
def update_graph(
    spot_price, strike_price, spot_range, increment_days, dte, 
    front_vol_initial, front_vol_final, back_vol_initial, back_vol_final,
    relative_value
):

    spot_range = [
        spot_price - spot_range, 
        spot_price + spot_range,
    ]
    
    dte = int(dte)
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

    return fig


###############################################################################
# Run app

app.run_server(debug=True, use_reloader=True) # Turn off reloader if inside Jupyter