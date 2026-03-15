#!/usr/bin/env python3
"""
Raspberry Pi Camera Capture and Communication Script
Captures images with PiCamera2 and sends them to laptop for analysis
"""

import time
import requests
import json
from picamera2 import Picamera2
from PIL import Image
import io
import os


class PiCameraController:
    def __init__(self, laptop_ip="http://127.0.0.1:5000", laptop_port=5000):
        """
        Initialize the Pi Camera controller

        Args:
            laptop_ip: IP address of the laptop running the analysis server
            laptop_port: Port number of the analysis server
        """
        self.laptop_url = f"http://{laptop_ip}:{laptop_port}"
        self.camera = None
        self.setup_camera()

    def setup_camera(self):
        """Initialize and configure the PiCamera2"""
        try:
            self.camera = Picamera2()
            # Configure camera for high resolution
            config = self.camera.create_still_configuration(main={"size": (3280, 2464)})
            self.camera.configure(config)
            self.camera.start()
            print("Camera initialized successfully")
            # Give camera time to adjust
            time.sleep(2)
        except Exception as e:
            print(f"Error setting up camera: {e}")
            raise

    def capture_image(self, filename="capture.jpg"):
        """
        Capture an image with the camera

        Args:
            filename: Name to save the image locally

        Returns:
            Path to the captured image
        """
        try:
            print("Capturing image...")
            self.camera.capture_file(filename)
            print(f"Image captured and saved as {filename}")
            return filename
        except Exception as e:
            print(f"Error capturing image: {e}")
            raise

    def send_image_for_analysis(self, image_path):
        """
        Send image to laptop for terrain analysis

        Args:
            image_path: Path to the image file

        Returns:
            Analysis results dictionary
        """
        try:
            print(f"Sending image to laptop at {self.laptop_url}...")

            with open(image_path, 'rb') as img_file:
                files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
                response = requests.post(
                    f"{self.laptop_url}/analyze",
                    files=files,
                    timeout=60
                )

            if response.status_code == 200:
                results = response.json()
                print("Analysis complete!")
                return results
            else:
                print(f"Error: Server returned status code {response.status_code}")
                return None

        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to laptop at {self.laptop_url}")
            print("Make sure the laptop server is running and IP address is correct")
            return None
        except Exception as e:
            print(f"Error sending image: {e}")
            return None

    def display_results(self, results):
        """Display the analysis results in a user-friendly format"""
        if not results:
            print("No results to display")
            return

        print("\n" + "=" * 60)
        print("TERRAIN ANALYSIS RESULTS")
        print("=" * 60)

        if results.get('landing_site'):
            landing = results['landing_site']
            n = results.get('candidates_count', 1)
            if n > 1:
                print(f"\n✓ Best Landing Site Found (chose best of {n} candidate areas):")
            else:
                print(f"\n✓ Best Landing Site Found!")
            print(f"  Location: ({landing['x']}, {landing['y']})")
            print(f"  Flatness Score: {landing['flatness_score']:.2f}")
            print(f"  Terrain Proximity: {landing['terrain_proximity']:.2f}")
        else:
            print("\n⚠ No suitable landing area detected.")
            if results.get('landing_site_message'):
                print(f"  {results['landing_site_message']}")
            print(
                "  Tips: improve lighting, point camera at flatter terrain, or adjust analyzer parameters on the laptop.")

        if results.get('craters'):
            print(f"\n✓ Found {len(results['craters'])} Crater(s):")
            for i, crater in enumerate(results['craters'], 1):
                print(f"\n  Crater {i}:")
                print(f"    Location: ({crater['x']}, {crater['y']})")
                print(f"    Radius: {crater['radius']:.1f} pixels")

                if results.get('landing_site'):
                    direction = crater['direction_from_landing']
                    distance = crater['distance_from_landing']
                    print(f"    From Landing Site: {distance:.1f} pixels {direction}")

        if results.get('navigation_instructions'):
            print(f"\n📡 NAVIGATION INSTRUCTIONS:")
            for instruction in results['navigation_instructions']:
                print(f"  • {instruction}")

        print("\n" + "=" * 60)

    def cleanup(self):
        """Clean up camera resources"""
        if self.camera:
            self.camera.stop()
            self.camera.close()
            print("Camera resources released")


def main():
    """Main execution function"""
    # Configuration - UPDATE THESE VALUES
    LAPTOP_IP = "192.168.1.100"  # Change to your laptop's IP address
    LAPTOP_PORT = 5000

    controller = None

    try:
        # Initialize camera controller
        controller = PiCameraController(laptop_ip=LAPTOP_IP, laptop_port=LAPTOP_PORT)

        # Capture image
        image_path = controller.capture_image("terrain_capture.jpg")

        # Send for analysis
        results = controller.send_image_for_analysis(image_path)

        # Display results
        if results:
            controller.display_results(results)
        else:
            print("Failed to get analysis results")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if controller:
            controller.cleanup()


if __name__ == "__main__":
    main()

