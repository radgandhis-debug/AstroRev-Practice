#!/usr/bin/env python3
"""
Laptop-Side Terrain Analysis Server
Receives images from Raspberry Pi and performs terrain analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from terrain_analyzer import TerrainAnalyzer
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize terrain analyzer
analyzer = TerrainAnalyzer()

# Create directory for received images
os.makedirs("received_images", exist_ok=True)


@app.route('/analyze', methods=['POST'])
def analyze_terrain():
    """
    Main endpoint for terrain analysis
    Receives image from Pi and returns analysis results
    """
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        # Save the received image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"received_images/capture_{timestamp}.jpg"
        file.save(image_path)

        print(f"Received image: {image_path}")

        # Read and analyze the image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Failed to read image'}), 400

        print("Starting terrain analysis...")

        # Preprocess image
        processed = analyzer.preprocess_image(image)

        # Find flat areas
        print("Finding flat landing areas...")
        flat_areas = analyzer.find_flat_areas(processed, min_size=100)
        print(f"Found {len(flat_areas)} potential landing areas")

        # Select best landing site (if multiple candidates, we choose the single best one)
        landing_site = analyzer.select_best_landing_site(flat_areas, processed)
        candidates_count = len(flat_areas)

        # Find craters
        print("Detecting craters...")
        craters = analyzer.find_craters(processed, min_radius=15, max_radius=60)
        print(f"Found {len(craters)} craters")

        # Calculate navigation instructions
        navigation_instructions = []
        if landing_site and craters:
            navigation_instructions = analyzer.calculate_navigation(landing_site, craters)

        # Message when no landing area found (for display on Pi)
        if not landing_site:
            landing_site_message = (
                "No suitable flat landing area detected. "
                "Try better lighting, a clearer view of the surface, or lower min_size in the analyzer."
            )
        else:
            landing_site_message = None

        # Prepare results
        results = {
            'status': 'success',
            'landing_site': landing_site,
            'candidates_count': candidates_count,  # how many flat areas were evaluated (0 = none, 1+ = we chose best)
            'landing_site_message': landing_site_message,
            'craters': craters,
            'navigation_instructions': navigation_instructions,
            'image_path': image_path,
            'analysis_timestamp': timestamp
        }

        print("Analysis complete!")
        if landing_site:
            print(
                f"Best landing site: {landing_site['x']}, {landing_site['y']} (chose best of {candidates_count} candidate(s))")
        else:
            print("No landing site found (no flat areas met the criteria)")
        print(f"Found {len(craters)} craters")
        create_visualization(image_path, results)

        return jsonify(results)

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'terrain_analyzer'})


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with usage information"""
    return jsonify({
        'service': 'CubeSat Terrain Analysis Server',
        'endpoints': {
            '/analyze': 'POST - Upload image for terrain analysis',
            '/health': 'GET - Health check',
            '/': 'GET - This information'
        },
        'usage': 'Send POST request to /analyze with image file'
    })


def create_visualization(image_path, results, output_path=None):
    """
    Create a visualization of the analysis results

    Args:
        image_path: Path to the original image
        results: Analysis results dictionary
        output_path: Path to save visualization (optional)
    """
    image = cv2.imread(image_path)
    if image is None:
        return

    # Draw landing site
    if results.get('landing_site'):
        landing = results['landing_site']
        print(f"This is: {landing}")
        cv2.circle(image, (landing['x'], landing['y']), 30, (0, 255, 0), 3)
        cv2.putText(image, 'LANDING SITE',
                    (landing['x'] - 80, landing['y'] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Draw craters


    # If no output path provided, create one automatically
    if output_path == None:
        base = os.path.splitext(os.path.basename(image_path))[0]
        output_path = f"received_images/{base}_annotated.jpg"

    cv2.imwrite(output_path, image)
    print(f"Visualization saved to {output_path}")


    return image


if __name__ == '__main__':
    print("=" * 60)
    print("CubeSat Terrain Analysis Server")
    print("=" * 60)
    print("\nServer starting...")
    print("Make sure your Raspberry Pi can reach this laptop's IP address")
    print("\nTo find your IP address:")
    print("  - Linux/Mac: ifconfig or ip addr")
    print("  - Windows: ipconfig")
    print("\nUpdate the LAPTOP_IP in pi_camera_capture.py with this address")
    print("\nServer will run on: http://127.0.0.1:5000")
    print("=" * 60)

    # Run the Flask server
    # Use 0.0.0.0 to allow connections from other devices on the network
    app.run(host='0.0.0.0', port=5001, debug=True)

