(() => {
    // Prevent accidentally creating multiple canvases.
    if (document.querySelector(".matrix-canvas")) {
        return;
    }

    // Create the canvas.
    const canvas = document.createElement("canvas");
    canvas.className = "matrix-canvas";
    canvas.setAttribute("aria-hidden", "true");

    document.body.prepend(canvas);

    const ctx = canvas.getContext("2d");

    if (!ctx) {
        canvas.remove();
        return;
    }

    // Characters used in the Matrix rain.
    const characters =
        "アイウエオカキクケコサシスセソタチツテトナニヌネノ" +
        "ハヒフヘホマミムメモヤユヨラリルレロワン" +
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    let width;
    let height;
    let fontSize;
    let columns;
    let streams = [];

    let lastFrame = 0;

    const frameInterval = 1000 / 30;

    // Generate a random character.
    function randomCharacter() {
        const index = Math.floor(Math.random() * characters.length);
        return characters[index];
    }

    // Generate a new falling stream.
    function createStream() {
        return {
            position: Math.random() * (height / fontSize),
            speed: 0.2 + Math.random() * 0.6,
            lastCell: -1
        };
    }

    // Adjust the canvas to the browser window.
    function resizeCanvas() {
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);

        width = window.innerWidth;
        height = window.innerHeight;

        canvas.width = Math.floor(width * pixelRatio);
        canvas.height = Math.floor(height * pixelRatio);

        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;

        ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);

        fontSize = Math.max(14, Math.min(20, Math.round(width / 100)));

        columns = Math.ceil(width / fontSize);

        streams = Array.from(
            { length: columns },
            () => createStream()
        );

        // Clear the previous image after resizing.
        ctx.clearRect(0, 0, width, height);
    }

    // Draw and animate the falling characters.
    function draw(timestamp) {
        requestAnimationFrame(draw);

        // Limit animation to approximately 30 frames per second.
        if (document.hidden || timestamp - lastFrame < frameInterval) {
            return;
        }

        lastFrame = timestamp;

        // Fade previously drawn characters without painting over the page.
        ctx.globalCompositeOperation = "destination-out";
        ctx.fillStyle = "rgba(0, 0, 0, 0.12)";
        ctx.fillRect(0, 0, width, height);

        ctx.globalCompositeOperation = "source-over";

        ctx.font = `${fontSize}px monospace`;
        ctx.textAlign = "center";

        for (let i = 0; i < columns; i++) {
            const stream = streams[i];

            const currentCell = Math.floor(stream.position);

            // Draw a new character when the stream advances a row.
            if (currentCell !== stream.lastCell) {
                const x = i * fontSize + fontSize / 2;
                const y = currentCell * fontSize;

                if (y >= 0 && y <= height) {
                    // Occasionally make the leading character brighter.
                    const isBright = Math.random() > 0.92;

                    ctx.fillStyle = isBright ? "#d7ffe0" : "#00ff41";
                    ctx.shadowColor = "#00ff41";
                    ctx.shadowBlur = isBright ? 14 : 8;

                    ctx.fillText(randomCharacter(), x, y);

                    ctx.shadowBlur = 0;
                }

                stream.lastCell = currentCell;
            }

            // Move the stream downward.
            stream.position += stream.speed;

            // Restart the stream after it leaves the screen.
            if (stream.position * fontSize > height + fontSize * 12) {
                stream.position = -Math.random() * 20;
                stream.speed = 0.2 + Math.random() * 0.6;
                stream.lastCell = -1;
            }
        }
    }

    // Initialize and start.
    resizeCanvas();

    window.addEventListener("resize", resizeCanvas);

    requestAnimationFrame(draw);
})();