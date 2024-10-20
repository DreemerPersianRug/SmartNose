import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import plotly.subplots as sp
import random
import init
from utils import PortScanner, SerialPortHandler
from utils import ProtocolHandler

available_ports = PortScanner.port_list()

availible_ports_list = []
for value in available_ports:
    availible_ports_list.append({"label": value, "value": value})

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
            className="statistics-container",
            children=[
                html.Div(
                    className="statistic",
                    children=[
                        dcc.Graph(
                            id=f'pie-chart-{i}',
                            figure={
                                'data': [
                                    go.Pie(
                                        labels=['Category A', 'Category B', 'Category C'],
                                        values=[random.randint(10, 100) for _ in range(3)],
                                        textinfo='value',
                                        hole=.4,
                                        marker=dict(colors=[f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})' for _ in range(3)])
                                    )
                                ],
                                'layout': go.Layout(
                                    title=f'Statistic {i+1}',
                                    height=200,
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                            }
                        )
                    ]
                ) for i in range(4)
            ]
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
                                html.Button('Pause Measurement', id='pause-button', n_clicks=0, className="pause"),
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
                                    options=availible_ports_list
                                
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
        html.Div(
            className="table-and-description-container",
            children=[
                html.Div(
                    className="table-container",
                    children=[
                        dash_table.DataTable(
                            id='report-table',
                            columns=[
                                {"name": "Sensor", "id": "sensor"},
                                {"name": "Min Value", "id": "min_value"},
                                {"name": "Max Value", "id": "max_value"},
                                {"name": "Avg Value", "id": "avg_value"},
                            ],
                            data=[
                                {"sensor": f"Sensor {i+1}", "min_value": random.randint(10, 50), "max_value": random.randint(51, 100), "avg_value": round(random.uniform(10, 100), 2)}
                                for i in range(4)
                            ],
                            style_table={'overflowX': 'auto', 'minHeight': '300px'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '5px',
                                'font-family': 'Lato, sans-serif',
                            },
                            style_header={
                                'backgroundColor': '#3498db',
                                'color': 'white',
                                'fontWeight': 'bold'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f2f2f2'
                                },
                                {
                                    'if': {'row_index': 'even'},
                                    'backgroundColor': 'white'
                                }
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="description-container",
                    children=[
                        html.H3("Measurement Summary"),
                        html.P("This table provides a summary of the measurements taken from the sensors. The data includes the minimum, maximum, and average values for each sensor. This information can be used to analyze the quality of the fuel and optimize fuel management strategies."),
                        html.P("For more detailed analysis, refer to the live graph above."),
                    ]
                )
            ]
        )
    ]
)

data_for_graph = []
colors = {}
is_measuring = False

@app.callback(
    Output('live-graph', 'figure'),
    [
        Input('graph-update', 'n_intervals'),
        Input('start-button', 'n_clicks'),
        Input('pause-button', 'n_clicks'),
        Input('mode-dropdown', 'value'),
        Input('device-dropdown', 'value')
    ],
    [State('countdown-container', 'style')]
)
def update_graph(n_intervals, start_clicks, stop_clicks, mode, device, current_style):
    global data_for_graph, colors, is_measuring

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-button' and not is_measuring:
        is_measuring = True
    elif button_id == 'pause-button' and is_measuring:
        is_measuring = False

    if is_measuring:
        serial = SerialPortHandler(init.logger, device)
        serial.open_serial_connection()

        data_from_serial = serial.read_data()
        protocol = ProtocolHandler(data_from_serial)
        bin_arr = protocol.process()
        values = list(map(ProtocolHandler.parse_elem, bin_arr))
        
        if (len(values) == len(list(zip(*data_for_graph)))) or (len(data_for_graph) == 0):
            data_for_graph.append(values)

    fig = sp.make_subplots(rows=4, cols=2, subplot_titles=[f'Sensor {i+1}' for i in range(len(values))])

    max_values = []
    min_values = []
    for i, series in enumerate(zip(*data_for_graph)):
        y_values = series
        max_values.append(max(y_values))
        min_values.append(min(y_values))
        x_values = [i for i in range(series.__len__())]
        if i not in colors:
            colors[i] = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
        row = (i // 2) + 1
        col = (i % 2) + 1
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name=f'Sensor {i+1}',
                line=dict(color=colors[i]),
                fill='tozeroy'
            ),
            row=row, col=col
        )

    fig.update_layout(
        title=dict(text=f'Live Fuel Analytics ({mode})', y=1, x=0.5, xanchor='center', yanchor='top'),
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='black'), 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, b=50, t=80, pad=4),
        height=1000
    )
    
    for i in range(len(values)):
        row = (i // 2) + 1
        col = (i % 2) + 1
        fig.update_xaxes(title_text='Time', range=[0, len(data_for_graph)], row=row, col=col, title_font=dict(size=11))
        fig.update_yaxes(title_text='Value', range=[min_values[i], max_values[i]], row=row, col=col, title_font=dict(size=11))

    return fig

if __name__ == "__main__":
    app.run_server(debug=False, host='127.0.0.1', port=8056)