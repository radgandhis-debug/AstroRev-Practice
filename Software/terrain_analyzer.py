"""
Terrain Analysis Module
Detects craters and selects a 15x15 km landing site
for a 364x210 image covering 130x75 km
"""

import cv2
import numpy as np
from typing import List, Dict, Optional


class TerrainAnalyzer:

    # image size
    IMAGE_WIDTH = 364
    IMAGE_HEIGHT = 210

    # map size
    AREA_WIDTH_KM = 130
    AREA_HEIGHT_KM = 75

    # landing zone
    LANDING_SIZE_KM = 15

    def __init__(self):

        self.km_per_pixel_x = self.AREA_WIDTH_KM / self.IMAGE_WIDTH
        self.km_per_pixel_y = self.AREA_HEIGHT_KM / self.IMAGE_HEIGHT

        self.landing_px = int(self.LANDING_SIZE_KM / self.km_per_pixel_x)

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray = cv2.equalizeHist(gray)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        return blurred

    def compute_gradient(self, image: np.ndarray) -> np.ndarray:

        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)

        gradient = cv2.magnitude(gx, gy)

        gradient = cv2.normalize(
            gradient, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.float32)

        return gradient

    def find_flat_areas(self, image: np.ndarray, min_size: int = None) -> List[Dict]:

        gradient = self.compute_gradient(image)
        # Backward compatibility with older callers using min_size
        # Landing window is fixed by mission design (≈42 px), so the argument is ignored
        _ = min_size

        window = self.landing_px

        step = 4

        height, width = gradient.shape

        results = []

        for y in range(0, height - window, step):

            for x in range(0, width - window, step):

                region = gradient[y:y + window, x:x + window]

                flatness = np.mean(region)

                flatness_score = 1 - (flatness / 255)

                results.append({
                    "x": x + window // 2,
                    "y": y + window // 2,
                    "flatness_score": float(flatness_score),
                    "area": window * window
                })

        results.sort(
            key=lambda r: r["flatness_score"],
            reverse=True
        )

        return results[:50]

    def select_best_landing_site(
        self,
        flat_areas: List[Dict],
        image: np.ndarray
    ) -> Optional[Dict]:

        if not flat_areas:
            return None

        best = flat_areas[0]

        return {
            "x": best["x"],
            "y": best["y"],
            "flatness_score": best["flatness_score"],
            "area": best["area"]
        }

    def find_craters(
        self,
        image: np.ndarray,
        min_radius: int = 5,
        max_radius: int = 50
    ) -> List[Dict]:

        edges = cv2.Canny(image, 40, 120)

        circles = cv2.HoughCircles(
            edges,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=20,
            param1=100,
            param2=20,
            minRadius=min_radius,
            maxRadius=max_radius
        )

        craters = []

        if circles is None:
            return craters

        circles = np.round(circles[0]).astype(int)

        height, width = image.shape

        for x, y, r in circles:

            if x < 0 or x >= width:
                continue

            if y < 0 or y >= height:
                continue

            craters.append({
                "x": int(x),
                "y": int(y),
                "radius": int(r)
            })

        return craters

    def calculate_navigation(
        self,
        landing_site: Dict,
        craters: List[Dict]
    ) -> List[str]:

        if landing_site is None:
            return []

        if not craters:
            return []

        lx = landing_site["x"]
        ly = landing_site["y"]

        directions = [
            "N", "NE", "E", "SE",
            "S", "SW", "W", "NW"
        ]

        instructions = []

        for i, crater in enumerate(craters, 1):

            dx = crater["x"] - lx
            dy = crater["y"] - ly

            distance = np.sqrt(dx * dx + dy * dy)

            angle = np.degrees(np.arctan2(dx, -dy))

            if angle < 0:
                angle += 360

            idx = int((angle + 22.5) / 45) % 8

            direction = directions[idx]

            crater["distance_from_landing"] = float(distance)
            crater["direction_from_landing"] = direction
            crater["angle_from_landing"] = float(angle)

            instructions.append(
                f"Crater {i}: Head {direction} for {distance:.1f} pixels ({angle:.1f}°)"
            )

        return instructions
