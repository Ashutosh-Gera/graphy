from flask import Flask, render_template, request, jsonify, Response
from graph import create_sample_graph
from algorithms import dfs, bfs
import plotly.graph_objs as go
import plotly
import json
import networkx as nx

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    data = request.get_json()
    algorithm = data['algorithm']
    G = create_sample_graph()
    start_node = 'A'  # Hardcoded for simplicity

    if algorithm == 'dfs':
        steps = dfs(G, start_node)
    elif algorithm == 'bfs':
        steps = bfs(G, start_node)
    else:
        return jsonify({'error': 'Invalid algorithm'})

    figure = create_visualization_frames(G, steps)
    
    # Serialize the figure using PlotlyJSONEncoder
    figure_json = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Return the serialized figure with the correct MIME type
    return Response(figure_json, mimetype='application/json')

def create_visualization_frames(G, steps):
    import plotly.graph_objs as go
    import networkx as nx

    pos = nx.spring_layout(G, seed=42)  # Fixed positions for consistency
    node_indices = list(G.nodes())

    # Prepare initial node positions
    node_x = []
    node_y = []
    for node in node_indices:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    # Initialize node colors
    initial_node_color = ['blue'] * len(node_indices)

    # Prepare initial node trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_indices,
        textposition='top center',
        marker=dict(
            color=initial_node_color,
            size=20,
            line=dict(width=2, color='black')
        ),
        hoverinfo='text'
    )

    # Prepare edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=2, color='#888'),  # Default color
            hoverinfo='none'
        )
        edge_traces.append(edge_trace)

    # Create frames for each step
    frames = []
    for step_num, step in enumerate(steps):
        visited_nodes = step['visited']
        current_node = step['current']
        traversed_edges = step.get('edges', [])

        # Update node colors
        frame_node_color = []
        for node in node_indices:
            if node == current_node:
                frame_node_color.append('green')  # Current node
            elif node in visited_nodes:
                frame_node_color.append('red')    # Visited nodes
            else:
                frame_node_color.append('blue')   # Unvisited nodes

        # Update edge colors
        frame_edge_traces = []
        for i, edge in enumerate(G.edges()):
            edge_color = 'blue'  # Default edge color
            if edge in traversed_edges or (edge[1], edge[0]) in traversed_edges:
                edge_color = 'red'  # Traversed edge
            edge_trace = go.Scatter(
                x=[pos[edge[0]][0], pos[edge[1]][0]],
                y=[pos[edge[0]][1], pos[edge[1]][1]],
                mode='lines',
                line=dict(width=2, color=edge_color),
                hoverinfo='none'
            )
            frame_edge_traces.append(edge_trace)

        # Create frame
        frame = go.Frame(
            data=frame_edge_traces + [
                go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers+text',
                    text=node_indices,
                    textposition='top center',
                    marker=dict(
                        color=frame_node_color,
                        size=20,
                        line=dict(width=2, color='black')
                    ),
                    hoverinfo='text'
                )
            ],
            name=f'Step{step_num}'
        )
        frames.append(frame)

    # Define layout with animation settings
    layout = go.Layout(
        title='Graph Algorithm Visualization',
        showlegend=False,
        hovermode='closest',
        updatemenus=[
            {
                'type': 'buttons',
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 1000, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 500, 'easing': 'quadratic-in-out'}
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }
        ],
        sliders=[{
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Step:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 500, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': [{
                'method': 'animate',
                'args': [
                    [f'Step{k}'],
                    {'frame': {'duration': 1000, 'redraw': True},
                     'transition': {'duration': 500, 'easing': 'quadratic-in-out'}}
                ],
                'label': str(k)
            } for k in range(len(frames))]
        }]
    )

    # Create the figure with initial data
    initial_edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=2, color='#888'),  # Default color
            hoverinfo='none'
        )
        initial_edge_traces.append(edge_trace)

    figure = go.Figure(
        data=initial_edge_traces + [node_trace],
        layout=layout,
        frames=frames
    )

    return figure



if __name__ == '__main__':
    app.run(debug=True)