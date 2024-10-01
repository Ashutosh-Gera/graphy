# app.py
from flask import Flask, render_template, request, jsonify, Response
from graph import create_sample_graph
from algorithms import dfs, bfs
import plotly.graph_objs as go
import plotly
import json
import networkx as nx

app = Flask(__name__)

# Color palette
COLORS = {
    'unvisited_node': '#1f77b4',  # Blue
    'visited_node': '#d62728',    # Red
    'current_node': '#2ca02c',    # Green
    'untraversed_edge': '#7f7f7f', # Gray
    'traversed_edge': '#17becf'   # Cyan
}

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

    pos = nx.spring_layout(G, seed=42, k=0.5)  # Fixed positions for consistency
    node_indices = list(G.nodes())

    # Prepare initial node positions
    node_x = []
    node_y = []
    for node in node_indices:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    # Initialize node colors
    initial_node_color = [COLORS['unvisited_node']] * len(node_indices)

    # Prepare initial node trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_indices,
        textposition='top center',
        marker=dict(
            color=initial_node_color,
            size=30,
            line=dict(width=2, color='black')
        ),
        hoverinfo='text',
        hovertext=['Node: {}'.format(node) for node in node_indices]
    )

    # Prepare edge traces
    initial_edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=2, color=COLORS['untraversed_edge']),
            hoverinfo='text',
            hovertext='Edge: {}-{}'.format(edge[0], edge[1])
        )
        initial_edge_traces.append(edge_trace)

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
                frame_node_color.append(COLORS['current_node'])  # Current node
            elif node in visited_nodes:
                frame_node_color.append(COLORS['visited_node'])    # Visited nodes
            else:
                frame_node_color.append(COLORS['unvisited_node'])   # Unvisited nodes

        # Update edge colors
        frame_edge_traces = []
        for edge in G.edges():
            edge_color = COLORS['untraversed_edge']  # Default edge color
            if edge in traversed_edges or (edge[1], edge[0]) in traversed_edges:
                edge_color = COLORS['traversed_edge']  # Traversed edge
            edge_trace = go.Scatter(
                x=[pos[edge[0]][0], pos[edge[1]][0], None],
                y=[pos[edge[0]][1], pos[edge[1]][1], None],
                mode='lines',
                line=dict(width=2, color=edge_color),
                hoverinfo='text',
                hovertext='Edge: {}-{}'.format(edge[0], edge[1])
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
                        size=30,
                        line=dict(width=2, color='black')
                    ),
                    hoverinfo='text',
                    hovertext=['Node: {}'.format(node) for node in node_indices]
                )
            ],
            name=f'Step{step_num}'
        )
        frames.append(frame)

    # Define layout with default animation settings
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
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
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
                ],
                'showactive': False,
                'x': 0.1,
                'y': 0,
                'xanchor': 'right',
                'yanchor': 'top'
            }
        ],
        sliders=[{
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 16, 'color': '#666'},
                'prefix': 'Step ',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': [{
                'method': 'animate',
                'args': [
                    [f'Step{k}'],
                    {'frame': {'duration': 500, 'redraw': True},
                     'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}
                ],
                'label': str(k)
            } for k in range(len(frames))]
        }]
    )

    # Create the figure with initial data
    figure = go.Figure(
        data=initial_edge_traces + [node_trace],
        layout=layout,
        frames=frames
    )

    return figure

if __name__ == '__main__':
    app.run(debug=True)
