import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import random
import init
from utils import PortScanner, SerialPortHandler
from utils import ProtocolHandler

available_ports = PortScanner.port_list()
ap = []
for value in available_ports:
    ap.append({"label": value, "value": value})

config = init.config.read()

if config["first_run"] == True:
    config["first_run"] = False
    init.config.write(config)

modes = []
for _, value in config["measurement_modes"].items():
    modes.append({"label": f"Time {value} sec", "value": value})

external_stylesheets = ['/assets/styles.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Fuel Analytics: Understand Your fuel!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚗", className="header-emoji"),
                html.H1(
                    children="Fuel Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the real-time quality of fuel, "
                    "monitor fuel consumption and efficiency, "
                    "optimize your fuel management strategy",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            className="graph-container",
            children=[
                html.Div(
                    className="graph",
                    children=[
                        dcc.Graph(id='live-graph', animate=True),
                        dcc.Interval(
                            id='graph-update',
                            interval=1*1000,  
                            n_intervals=0
                        ),
                    ]
                ),
                html.Div(
                    className="controls",
                    children=[
                        html.Div(
                            className="button-container",
                            children=[
                                html.Button('Start Measurement', id='start-button', n_clicks=0, className="start"),
                                html.Button('Stop Measurement', id='stop-button', n_clicks=0, className="stop"),
                            ]
                        ),
                        html.Div(
                            className="dropdown-container",
                            children=[
                                dcc.Dropdown(
                                    id='mode-dropdown',
                                    options=modes,
                                    value=modes[0]['value'],
                                )
                            ]
                        ),
                        html.Div(
                            className="dropdown-container-devices",
                            children=[
                                dcc.Dropdown(
                                    id="device-dropdown",
                                    options=ap,
                                    value=ap[-1]['value']
                                )
                            ]
                        ),
                        html.Div(
                            id='countdown-container',
                            className='countdown-container',
                            children=[
                                html.Div(id='countdown', className='countdown')
                            ]
                        )
                    ]
                )
            ]
        ),
    ]
)

data = []
colors = {}
countdown_value = config["timeout_under_measure"]

""" @app.callback(
    [Output('countdown-container', 'style'),
    Output('countdown', 'children')],
    [Input('start-button', 'n_clicks')],
    [State('countdown-container', 'style')]
)
def start_countdown(n_clicks, current_style):
    global countdown_value
    print("start_countdown called")
    if n_clicks > 0:
        countdown_value = config["timeout_under_measure"]
        print("Countdown started")
        return {'display': 'flex', 'width': '100%', 'height': '50px'}, str(countdown_value)
    return current_style, str(countdown_value)

@app.callback(
    Output('countdown', 'children'),
    [Input('graph-update', 'n_intervals')],
    [State('countdown-container', 'style')]
)
def update_countdown(n_intervals, current_style):
    global countdown_value
    print("update_countdown called")
    if current_style.get('display') == 'flex':
        if countdown_value > 0:
            countdown_value -= 1
            print("Countdown updated:", countdown_value)
            return str(countdown_value)
        else:
            print("Countdown finished")
            return ''
    return str(countdown_value) """

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'),
    Input('start-button', 'n_clicks'),
    Input('stop-button', 'n_clicks'),
    Input('mode-dropdown', 'value'),
    Input('device-dropdown', 'value')],
    [State('countdown-container', 'style')]
)
def update_graph(n_intervals, start_clicks, stop_clicks, mode, device, current_style):
    global data, colors

    serial = SerialPortHandler(init.logger, device)
    serial.open_serial_connection()

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #if button_id == 'start-button' and start_clicks > stop_clicks and current_style.get('display') != 'flex':
        data_1 = serial.read_data()
        protocol = ProtocolHandler(data_1)
        bin_arr = protocol.process()
        values = list(map(ProtocolHandler.parse_elem, bin_arr))
        data.append(values)
        print(data)
    #elif button_id == 'stop-button' and stop_clicks > start_clicks:
    #    data = []  

    traces = []
    for i, series in enumerate(data):
        y_values = series
        x_values = [i for i in range(series.__len__())]
        if i not in colors:
            colors[i] = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
        trace = go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name=f'Sensor {i+1}',
            line=dict(color=colors[i]),
            fill='tozeroy'  
        )
        traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis=dict(title='Time', range=[min(x_values), max(x_values)]),
            yaxis=dict(title='Value', range=[min(y_values), max(y_values)]),
            title=dict(text=f'Live Fuel Analytics ({mode})', y=0.95, x=0.5, xanchor='center', yanchor='top'),
            plot_bgcolor='rgba(0,0,0,0)',  
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='black'), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, b=50, t=80, pad=4)
        )
    }

if __name__ == "__main__":
    app.run_server(debug=False, host='127.0.0.1', port=8055)