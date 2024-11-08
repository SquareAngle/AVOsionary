from flask import (
    Flask, render_template, request, redirect, url_for, session, jsonify)
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
import numpy as np
import io
import base64
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/recognize', methods=['GET'])
def recognize_get():
    print('in recognize get')
    return render_template('recognize.html')

@app.route('/recognize', methods=['POST'])
def recognize_post(): 
    print("TEST")
    pixels = request.form['pixels']
    pixels = pixels.split(',')
    image = np.array(pixels).astype(float).reshape(1, 50, 50, 1)

    model = keras.models.load_model('numbers4.keras')
    pred = np.argmax(model.predict(image), axis=-1) 
    print(f'Prediction Value: {pred[0]}')

    conv_layers = []
    model_weights = []
    for layer in model.layers:
        get_conv_models_and_weights(layer, conv_layers, model_weights)
    
    outputs = []
    names = []
    for layer in conv_layers: 
        image = layer(image)
        outputs.append(image)
        names.append(str(layer))

    processed = []
    for feature_map in outputs:
        feature_map = tf.squeeze(feature_map, axis=0) # remove the batch dimension
        num_filters = feature_map.shape[-1]

        for j in range(num_filters):
            single_filter_map = feature_map[:, :, j].numpy()
            processed.append(single_filter_map)

    processed_images = []
    for i, fm in enumerate(processed):
        fig, ax = plt.subplots(figsize=(4,4))
        ax.imshow(fm, cmap='viridis')
        ax.axis("off")
        ax.set_title(f'Feature Map {i}', fontsize=10)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        processed_images.append(img_base64)

    return jsonify(pred=pred[0].item(), images=processed_images)

def get_conv_models_and_weights(layer, conv_layers, model_weights):
    if isinstance(layer, layers.Conv2D):
        model_weights.append(layer.get_weights())
        conv_layers.append(layer)
    elif hasattr(layer, 'layers'):
        for sub_layer in layer.layers:
            get_conv_models_and_weights(sub_layer, conv_layers, model_weights)

if __name__ == '__main__':
    app.run(debug=True)