let canvas
let context
let paint
let clickX = []
let clickY = []
let clickDrag = []

function startCanvas() {
 canvas = document.getElementById("canvas")
 context = canvas.getContext("2d")

 context.strokeStyle = "#000000"
 context.lineJoin = "round"
 context.lineWidth = 20

 canvas.addEventListener("touchstart", function (e) {
   var touch = e.touches[0]
   var mouseEvent = new MouseEvent("mousedown", {
     clientX: touch.clientX,
     clientY: touch.clientY,
   })
   canvas.dispatchEvent(mouseEvent)
 })

 canvas.addEventListener("touchmove", function (e) {
   var touch = e.touches[0]
   var mouseEvent = new MouseEvent("mousemove", {
     clientX: touch.clientX,
     clientY: touch.clientY,
   })
   canvas.dispatchEvent(mouseEvent)
 })

 canvas.addEventListener("touchend", function (e) {
   var mouseEvent = new MouseEvent("mouseup")
   canvas.dispatchEvent(mouseEvent)
 })

 $('#canvas').mousedown(function (e) {
   paint = true
   addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, false)
   drawCanvas()
 })

 $('#canvas').mousemove(function (e) {
   if (paint) {
     addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true)
     drawCanvas()
   }
 })

 $('#canvas').mouseup(function (e) {
   paint = false
   drawCanvas()
 })

 $('#canvas').mouseleave(function (e) {
   paint = false
 })
}

function addClick(x, y, dragging) {
 clickX.push(x)
 clickY.push(y)
 clickDrag.push(dragging)
}

function drawCanvas() {
    for(let i = 0; i < clickX.length; i++) {
        context.beginPath()
        if (clickDrag[i] && i) {
            context.moveTo(clickX[i - 1], clickY[i - 1])
        } else {
            context.moveTo(clickX[i] - 1, clickY[i])
        }
        context.lineTo(clickX[i], clickY[i])
        context.closePath()
        context.stroke()
    }
}

function resetCanvas() {
    clickX = []
    clickY = []
    clickDrag = []
    context.clearRect(0, 0, canvas.width, canvas.height)
}

function getPixels() {
    let rawPixels = context.getImageData(0, 0, 200, 200).data
    let _pixels = []
    let pixels = []

    for (i = 0; i < rawPixels.length; i += 4) {
        _pixels.push(rawPixels[i + 3])
    }

    for (i = 0; i < _pixels.length; i += 800) {
        for (j = 0; j < 200; j += 4) {
            pixels.push(_pixels[i + j])
        }
    }

    return pixels
}

function regAction() {
    let pixels = getPixels();
    document.getElementById('pixels').value = pixels; // Still set the hidden input if needed
    // Create a FormData object
    const formData = new FormData(document.getElementById("practice-form"));

    // Use Fetch API to send form data without reloading the page
    fetch ('/recognize', {
        method: 'POST',
        body: formData
    })

    .then(response => {
        if (response.ok) {
            return response.json(); // Parse JSON response
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data);
        displayPrediction(data.pred, data.images)
      })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function displayPrediction(pred, images) {
    const outputDiv = document.getElementById('prediction-output');

    // clear previous content
    outputDiv.innerHTML = `<h2>Prediction: ${pred}</h2>`;

    // display each feature map image
    images.forEach((imgBase64, index) => {
        const imgElement = document.createElement('img');
        imgElement.src = `data:image/png:base64,${imgBase64}`;
        imgElement.alt = `Feature Map ${index + 1}`;
        imgElement.style.margin = '10px';
        imgElement.style.border = '1px solid #ddd';
        outputDiv.appendChild(imgElement);
    });
}