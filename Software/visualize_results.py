#!/usr/bin/env python3
"""
Visualization Helper Script
Creates annotated images showing landing sites and craters
"""

import cv2
import json
import sys
import os
from terrain_analyzer import TerrainAnalyzer


def visualize_analysis(image_path, results_path=None, output_path=None):
    """
    Create a visualization of analysis results

    Args:
        image_path: Path to the original image
        results_path: Path to JSON results file (optional, can pass results dict directly)
        output_path: Path to save visualization (default: adds _annotated.jpg)
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return None

    # Load results
    if results_path:
        with open(results_path, 'r') as f:
            results = json.load(f)
    else:
        print("Error: Please provide results_path or pass results dictionary")
        return None

    # Draw landing site (or note if none found)
    if results.get('landing_site'):
        landing = results['landing_site']
        x, y = landing['x'], landing['y']

        # Draw large circle for landing site
        cv2.circle(image, (x, y), 50, (0, 255, 0), 4)
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        # Add label
        label = f"LANDING SITE (Score: {landing['flatness_score']:.2f})"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(image,
                      (x - text_size[0] // 2 - 10, y - 70),
                      (x + text_size[0] // 2 + 10, y - 40),
                      (0, 255, 0), -1)
        cv2.putText(image, label,
                    (x - text_size[0] // 2, y - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    else:
        # No landing site: show message on image
        msg = "No suitable landing area detected"
        (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        x_center = image.shape[1] // 2
        cv2.rectangle(image, (x_center - tw // 2 - 15, 20), (x_center + tw // 2 + 15, 55), (0, 0, 0), -1)
        cv2.putText(image, msg, (x_center - tw // 2, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

    # Draw craters
    if results.get('craters'):
        for i, crater in enumerate(results['craters'], 1):
            x, y, r = crater['x'], crater['y'], crater['radius']

            # Draw crater circle
            cv2.circle(image, (x, y), r, (0, 0, 255), 3)
            cv2.circle(image, (x, y), 3, (0, 0, 255), -1)

            # Add label
            label = f"Crater {i} (R={r})"
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(image,
                          (x - text_size[0] // 2 - 5, y - r - 35),
                          (x + text_size[0] // 2 + 5, y - r - 10),
                          (0, 0, 255), -1)
            cv2.putText(image, label,
                        (x - text_size[0] // 2, y - r - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Draw line from landing site to crater
            if results.get('landing_site'):
                landing = results['landing_site']
                cv2.line(image,
                         (landing['x'], landing['y']),
                         (x, y),
                         (255, 255, 0), 2)

                # Add distance and direction text
                if 'distance_from_landing' in crater:
                    dist = crater['distance_from_landing']
                    direction = crater.get('direction_from_landing', '')
                    mid_x = (landing['x'] + x) // 2
                    mid_y = (landing['y'] + y) // 2
                    dist_label = f"{direction} {dist:.0f}px"
                    cv2.putText(image, dist_label,
                                (mid_x, mid_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Save or display
    if output_path is None:
        output_path = image_path.replace('.jpg', '_annotated.jpg').replace('.png', '_annotated.png')

    cv2.imwrite(output_path, image)
    print(f"Visualization saved to: {output_path}")

    return image


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python visualize_results.py <image_path> [results_json_path] [output_path]")
        print("\nExample:")
        print("  python visualize_results.py image.jpg results.json")
        print("  python visualize_results.py image.jpg results.json output.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    results_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    if results_path is None:
        # Try to find results in received_images directory
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        results_path = f"received_images/{base_name}_results.json"
        if not os.path.exists(results_path):
            print(f"Error: Could not find results file. Please specify: {sys.argv[0]} <image> <results.json>")
            sys.exit(1)

    visualize_analysis(image_path, results_path, output_path)


if __name__ == "__main__":
    main()

