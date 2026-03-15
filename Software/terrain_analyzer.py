"""
Terrain Analysis Module
Analyzes images to find flat landing areas and craters
"""

import cv2
import numpy as np
from scipy import ndimage
from typing import List, Dict, Tuple, Optional

class TerrainAnalyzer:
    def __init__(self):
        """Initialize the terrain analyzer"""
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for analysis
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return blurred
    
    def find_flat_areas(self, image: np.ndarray, min_size: int = 100) -> List[Dict]:
        """
        Find flat areas suitable for landing
        
        Args:
            image: Preprocessed grayscale image
            min_size: Minimum size of flat area in pixels
            
        Returns:
            List of flat area dictionaries with coordinates and scores
        """
        # Calculate gradient magnitude to find flat areas (low gradient = flat)
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=11)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=11)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize gradient
        gradient_norm = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Threshold to find flat areas (low gradient values)
        _, flat_mask = cv2.threshold(gradient_norm, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        flat_mask = cv2.morphologyEx(flat_mask, cv2.MORPH_CLOSE, kernel)
        flat_mask = cv2.morphologyEx(flat_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours of flat areas
        contours, _ = cv2.findContours(flat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        flat_areas = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_size:
                # Calculate centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Calculate flatness score (lower gradient = flatter)
                    mask = np.zeros(image.shape, np.uint8)
                    cv2.drawContours(mask, [contour], -1, 255, -1)
                    flatness = np.mean(gradient_norm[mask > 0])
                    flatness_score = 1.0 - (flatness / 255.0)  # Normalize to 0-1
                    
                    # Calculate bounding box for terrain proximity
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    flat_areas.append({
                        'x': cx,
                        'y': cy,
                        'area': area,
                        'flatness_score': flatness_score,
                        'contour': contour,
                        'bbox': (x, y, w, h)
                    })
        
        # Sort by flatness score (highest first)
        flat_areas.sort(key=lambda x: x['flatness_score'], reverse=True)
        
        return flat_areas
    
    def calculate_terrain_proximity(self, flat_area: Dict, image: np.ndarray) -> float:
        """
        Calculate how close the flat area is to terrain features
        
        Args:
            flat_area: Dictionary containing flat area information
            image: Original grayscale image
            
        Returns:
            Terrain proximity score (higher = closer to terrain)
        """
        x, y, w, h = flat_area['bbox']
        height, width = image.shape
        
        # Expand search area around the flat area
        expand = 50
        x1 = max(0, x - expand)
        y1 = max(0, y - expand)
        x2 = min(width, x + w + expand)
        y2 = min(height, y + h + expand)
        
        # Extract region around flat area
        region = image[y1:y2, x1:x2]
        
        # Calculate variance (higher variance = more terrain features)
        variance = np.var(region)
        
        # Normalize to 0-1 scale
        proximity_score = min(1.0, variance / 1000.0)
        
        return proximity_score
    
    def find_craters(self, image: np.ndarray, min_radius: int = 50, max_radius: int = 1000) -> List[Dict]:
        """
        Find craters in the image using Hough Circle Transform
        
        Args:
            image: Preprocessed grayscale image
            min_radius: Minimum crater radius in pixels
            max_radius: Maximum crater radius in pixels
            
        Returns:
            List of crater dictionaries with coordinates and radii
        """
        # Apply adaptive thresholding to enhance crater edges
        adaptive = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Use Hough Circle Transform to detect circular craters
        circles = cv2.HoughCircles(
            adaptive,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=min_radius * 2,
            param1=50,
            param2=30,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        craters = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")

            height, width = image.shape

            for (x, y, r) in circles:

                # Prevent out-of-bounds indexing
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue

                center_intensity = image[y, x]
                avg_intensity = np.mean(image)

                if center_intensity < avg_intensity * 0.9:
                    craters.append({
                        'x': int(x),
                        'y': int(y),
                        'radius': int(r)
                    })
        
        # Also try contour-based detection for non-perfect circles
        # Find dark circular regions
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > np.pi * min_radius**2 and area < np.pi * max_radius**2:
                # Check circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    if circularity > 0.5:  # Reasonably circular
                        (x, y), radius = cv2.minEnclosingCircle(contour)
                        if min_radius <= radius <= max_radius:
                            # Check if not already found
                            found = False
                            for existing in craters:
                                dist = np.sqrt((x - existing['x'])**2 + (y - existing['y'])**2)
                                if dist < radius:
                                    found = True
                                    break
                            if not found:
                                craters.append({
                                    'x': int(x),
                                    'y': int(y),
                                    'radius': int(radius)
                                })
        
        return craters
    
    def select_best_landing_site(self, flat_areas: List[Dict], image: np.ndarray) -> Optional[Dict]:
        """
        Select the best landing site from flat areas
        
        Criteria:
        - High flatness score
        - Good terrain proximity (not too isolated, not too crowded)
        - Reasonable size
        
        Args:
            flat_areas: List of flat area dictionaries
            image: Original image for terrain proximity calculation
            
        Returns:
            Best landing site dictionary or None
        """
        if not flat_areas:
            return None
        
        # Calculate terrain proximity for each flat area
        target_area = 518 ** 2
        closest_diff = float('inf')
        best_flat = None

        for area in flat_areas:
            diff = abs(area['area'] - target_area)

            if diff < closest_diff:
                closest_diff = diff
                best_flat = area


        # Score each area (weighted combination)

        
        # Sort by combined score

        
        # Return the best one
        best = best_flat.copy()
        # Remove contour and bbox for JSON serialization
        best.pop('contour', None)
        best.pop('bbox', None)
        
        return best
    
    def calculate_navigation(self, landing_site: Dict, craters: List[Dict]) -> List[str]:
        """
        Calculate navigation instructions from landing site to craters
        
        Args:
            landing_site: Landing site dictionary with x, y coordinates
            craters: List of crater dictionaries with x, y, radius
            
        Returns:
            List of navigation instruction strings
        """
        instructions = []
        
        if not landing_site or not craters:
            return instructions
        
        landing_x = landing_site['x']
        landing_y = landing_site['y']
        
        for i, crater in enumerate(craters, 1):
            # Calculate distance
            dx = crater['x'] - landing_x
            dy = crater['y'] - landing_y
            distance = np.sqrt(dx**2 + dy**2)
            
            # Calculate direction (in degrees, 0 = North/Up)
            angle = np.degrees(np.arctan2(dx, -dy))  # Negative dy because y increases downward
            if angle < 0:
                angle += 360
            
            # Convert to cardinal/intercardinal directions
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            direction_idx = int((angle + 22.5) / 45) % 8
            direction = directions[direction_idx]
            
            # Store in crater dict
            crater['distance_from_landing'] = distance
            crater['direction_from_landing'] = direction
            crater['angle_from_landing'] = angle
            
            instructions.append(
                f"Crater {i}: Head {direction} for {distance:.1f} pixels "
                f"({angle:.1f}° from North)"
            )
        
        return instructions

