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

    layers_list = []
    weights_list = []
    names_list = []
    # Get all layers and their names
    for layer in model.layers:
        get_layers(layer, layers_list, weights_list, names_list)
    # Keep track of current layer output
    current_output = image
    
    outputs = []
    labels = []
    # Process each layer and collect outputs
    for i, layer in enumerate(layers_list): 
        if isinstance(layer, (layers.Conv2D, layers.MaxPooling2D, layers.Dropout)):
            # Process the current layer with the previous layer's output
            current_output = layer(current_output, training=False) # Set training=False for consistent results
            outputs.append(current_output)
            labels.append(names_list[i])
        elif isinstance(layer, layers.Flatten):
            current_output = layer(current_output)
            outputs.append(current_output)
            labels.append("Flatten")

    processed_images = []

    for i, feature_map in enumerate(outputs):
        if len(feature_map.shape) == 2: # Flattened output
            single_filter_map = feature_map.numpy()
            fig, ax = plt.subplots(figsize=(4,4))
            ax.bar(np.arange(len(single_filter_map[0])), single_filter_map[0])
            ax.set_xlabel('Index')
            ax.set_ylabel('Value')
            ax.set_title(f'{labels[i]} - Flattened Layer')
        else: # Feature maps from Conv2D or MaxPooling2D
            feature_map = tf.squeeze(feature_map, axis=0) # Remove batch dimension
            num_filters = feature_map.shape[-1]

            # Calculate grid size
            grid_size = int(np.ceil(np.sqrt(num_filters)))
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(12, 12))

            # Make axes 2D if it isn't already
            if num_filters == 1:
                axes = np.array([[axes]])
            elif grid_size == 1:
                axes = np.array([axes])

            # Plot each filter
            for filter_idx in range(num_filters):
                row = filter_idx // grid_size
                col = filter_idx % grid_size
                single_filter_map = feature_map[:, :, filter_idx].numpy()
                axes[row, col].imshow(single_filter_map, cmap='viridis')
                axes[row, col].axis('off')
            
            # Turn off empty subplots
            for j in range(num_filters, grid_size * grid_size):
                row = j // grid_size
                col = j % grid_size
                axes[row, col].axis('off')

            plt.suptitle(f'{labels[i]} - Feature Maps')
        
        # Save the figure
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        processed_images.append(img_base64)

    return jsonify(pred=pred[0].item(), images=processed_images)

def get_layers(layer, layers_list, weights_list, names_list):
    if isinstance(layer, layers.Conv2D):
        weights_list.append(layer.get_weights())
        layers_list.append(layer)
        names_list.append(f"Conv2D_{layer.name}")
    elif isinstance(layer, layers.MaxPooling2D):
        layers_list.append(layer)
        names_list.append(f"MaxPool_{layer.name}")
    elif isinstance(layer, layers.Dropout):
        layers_list.append(layer)
        names_list.append(f"Dropout_{layer.name}")
    elif isinstance(layer, layers.Dense):
        layers_list.append(layer)
        names_list.append(f"Dense_{layer.name}")
    elif hasattr(layer, 'layers'):
        for sub_layer in layer.layers:
            get_layers(sub_layer, layers_list, weights_list, names_list)

if __name__ == '__main__':
    app.run(debug=True)