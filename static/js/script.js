function runAlgorithm(algorithm) {
    fetch('/run_algorithm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'algorithm': algorithm })
    })
    .then(response => response.json())
    .then(figure => {
        // Render the graph
        Plotly.react('graph', figure).then(() => {
            // Start the animation automatically
            Plotly.animate('graph', null, {
                frame: { duration: 1000, redraw: true },
                transition: { duration: 500, easing: 'quadratic-in-out' }
            });
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
