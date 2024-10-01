// static/js/script.js

let animationSpeed = 1000; // Default speed in milliseconds
let isPlaying = false;

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
            // Store the figure for later use
            window.currentFigure = figure;
            // Start the animation automatically
            playAnimation();
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function playAnimation() {
    if (window.currentFigure) {
        isPlaying = true;
        Plotly.animate('graph', null, {
            frame: { duration: animationSpeed, redraw: true },
            transition: { duration: animationSpeed / 2, easing: 'quadratic-in-out' },
            mode: 'immediate'
        });
    }
}

function pauseAnimation() {
    if (window.currentFigure) {
        isPlaying = false;
        Plotly.animate('graph', null, {
            frame: { duration: 0, redraw: false },
            transition: { duration: 0 },
            mode: 'immediate'
        });
    }
}

function setAnimationSpeed(speedLevel) {
    // Invert the speed level to calculate animationSpeed
    // map speedLevel to an animationSpeed (duration in ms) between maxDuration and minDuration
    const minDuration = 200;  // Fastest speed (shortest duration)
    const maxDuration = 2000; // Slowest speed (longest duration)

    // Calculate the animationSpeed based on the speedLevel
    animationSpeed = maxDuration - ((speedLevel - 1) * (maxDuration - minDuration) / 9);

    animationSpeed = parseInt(animationSpeed);

    // Update the speed label
    let speedLabel;
    if (speedLevel <= 3) {
        speedLabel = 'Slow';
    } else if (speedLevel <= 7) {
        speedLabel = 'Medium';
    } else {
        speedLabel = 'Fast';
    }
    document.getElementById('speedLabel').innerText = speedLabel;

    if (isPlaying) {
        playAnimation();
    }
}

// Add event listener for frame updates
document.getElementById('graph').on('plotly_animated', function(eventData) {
    let frameNumber = eventData.frame;
    let stepInfoDiv = document.getElementById('step-info');
    if (window.currentFigure && window.currentFigure.frames && window.currentFigure.frames[frameNumber]) {
        let frameName = window.currentFigure.frames[frameNumber].name;
        stepInfoDiv.innerHTML = `<h5>Current Step: ${frameName}</h5>`;
    }
});
