document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const character = document.getElementById('character');
    const multiplierDisplay = document.querySelector('.multiplier-display');
    const signalButton = document.querySelector('.signal-button');
    const gameContainer = document.querySelector('.game-container');
    const pathLine = document.querySelector('.path-line');
    const pathFill = document.querySelector('.path-fill');
    
    let gameActive = false;
    let currentGameId = null;
    let currentMultiplier = 1.00;
    let lastPoints = [];
    
    // Game configuration
    const config = {
        containerWidth: gameContainer.clientWidth,
        containerHeight: gameContainer.clientHeight,
        targetX: gameContainer.clientWidth * 0.7, // 70% of container width
        targetY: gameContainer.clientHeight * 0.7, // 70% of container height
        horizontalSpeed: 1, // Constant horizontal speed
        verticalStartSpeed: 1.5, // Starting vertical speed
        verticalEndSpeed: 0.5 // Ending vertical speed
    };

    function getVerticalSpeed(progress) {
        // Linear interpolation between start and end speed based on progress
        return config.verticalStartSpeed + (config.verticalEndSpeed - config.verticalStartSpeed) * progress;
    }

    function updatePath(progress) {
        // Calculate vertical position with dynamic speed
        let verticalProgress = 0;
        const steps = 100;
        const dt = progress / steps;
        
        // Numerical integration for vertical position
        for (let i = 0; i < progress * steps; i++) {
            const p = i / steps;
            verticalProgress += getVerticalSpeed(p) * dt;
        }
        
        // Calculate positions
        const horizontalProgress = progress * config.horizontalSpeed;
        const x = config.targetX * Math.min(horizontalProgress, 1);
        const y = config.targetY * Math.min(verticalProgress, 1);

        // Store current point
        const currentPoint = {
            x: x,
            y: config.containerHeight - (config.targetY * verticalProgress)
        };

        // Update points array
        if (progress === 0) {
            lastPoints = [];
        } else {
            lastPoints.push(currentPoint);
        }

        // Create path for line and fill
        const linePath = lastPoints.map((point, i) => 
            `${i === 0 ? 'M' : 'L'} ${point.x},${point.y}`
        ).join(' ');

        // Create fill path that extends to bottom
        const fillPath = `
            M 0,${config.containerHeight} 
            ${linePath} 
            L ${x},${config.containerHeight} 
            Z
        `;

        // Update path with stroke and fill
        pathLine.style.width = `${x}px`;
        pathLine.style.height = `${config.containerHeight}px`;
        pathLine.innerHTML = `<svg width="100%" height="100%" style="position: absolute; left: 0; top: 0;">
            <path d="${fillPath}" fill="rgba(162, 155, 254, 0.1)"/>
            <path d="${linePath}" stroke="#a29bfe" stroke-width="4" fill="none"/>
        </svg>`;

        // Remove separate fill element
        pathFill.style.display = 'none';

        // Update character position
        character.style.setProperty('--x', `${x}px`);
        character.style.setProperty('--y', `${-y}px`);
        
        // Adjust rotation based on current position and vertical speed
        const rotationProgress = Math.max(horizontalProgress, verticalProgress);
        const speedFactor = getVerticalSpeed(progress) / config.verticalStartSpeed;
        character.style.setProperty('--rotation', `${30 * (1 - rotationProgress) * speedFactor}deg`);
    }

    function startGame() {
        if (gameActive) return;
        
        gameActive = true;
        signalButton.textContent = 'ЗАБРАТЬ';
        lastPoints = [];
        
        // Reset character position and path
        character.style.transform = 'translate(0, 0) rotate(30deg)';
        character.classList.remove('flying', 'crashed', 'cashed-out');
        updatePath(0);
        
        // Reset multiplier display color
        multiplierDisplay.style.color = '#a29bfe';
        
        // Start new game on server
        socket.emit('start_game', {}, (response) => {
            currentGameId = response.game_id;
        });
    }

    function stopGame() {
        if (!gameActive || !currentGameId) return;
        
        socket.emit('stop_game', { game_id: currentGameId }, (response) => {
            if (response.success) {
                // Move character off screen to the top right
                character.classList.add('cashed-out');
                character.style.setProperty('--x', `${config.containerWidth * 1.5}px`);
                character.style.setProperty('--y', `${-config.containerHeight * 1.5}px`);
                character.style.setProperty('--rotation', '-45deg');
                
                // Reset game state
                gameActive = false;
                currentGameId = null;
                signalButton.textContent = 'ПОЛУЧИТЬ СИГНАЛ';
            }
        });
    }

    function handleGameCrash(data) {
        if (!gameActive) return;
        
        gameActive = false;
        currentGameId = null;
        signalButton.textContent = 'ПОЛУЧИТЬ СИГНАЛ';
        
        // Keep character at 70% position
        character.classList.add('crashed');
        character.style.setProperty('--x', `${config.targetX}px`);
        character.style.setProperty('--y', `${-config.targetY}px`);
        character.style.setProperty('--rotation', '0deg');
        
        // Visual feedback in green
        multiplierDisplay.style.color = '#4cd137';
        multiplierDisplay.textContent = `ВАШ СИГНАЛ x${data.crash_point}`;
    }

    // Event Listeners
    signalButton.addEventListener('click', () => {
        if (!gameActive) {
            startGame();
        } else {
            stopGame();
        }
    });

    // Socket events
    socket.on('game_update', (data) => {
        if (!gameActive || data.game_id !== currentGameId) return;
        
        currentMultiplier = data.multiplier;
        multiplierDisplay.textContent = `x${currentMultiplier.toFixed(2)}`;
        
        // Calculate progress based on multiplier
        const progress = Math.min((currentMultiplier - 1) / 0.2, 1);
        character.classList.add('flying');
        updatePath(progress);
    });

    socket.on('game_end', (data) => {
        if (data.crashed) {
            handleGameCrash(data);
        }
    });
});
