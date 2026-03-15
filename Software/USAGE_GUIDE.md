# Complete Usage Guide - CubeSat Terrain Analysis System

This guide explains every file in the project and how to use the complete system.

---

## 📁 Project Files Overview

### Core Python Scripts

#### 1. `laptop_analyzer.py` ⭐ **REQUIRED**
**Purpose:** Flask web server that runs on your laptop to analyze terrain images.

**What it does:**
- Receives images from Raspberry Pi via HTTP POST requests
- Analyzes images to find landing sites and craters
- Returns analysis results as JSON
- Saves received images to `received_images/` directory
- Provides health check endpoint at `/health`

**How to use:**
```bash
python laptop_analyzer.py
```

**What you'll see:**
- Server starts on `http://0.0.0.0:5000`
- Waits for images from Raspberry Pi
- Prints analysis progress and results
- Saves each received image with timestamp

**Endpoints:**
- `POST /analyze` - Upload image for analysis
- `GET /health` - Check if server is running
- `GET /` - Service information

**Requirements:** Must run on laptop/server with network access

---

#### 2. `pi_camera_capture.py` ⭐ **REQUIRED**
**Purpose:** Raspberry Pi script that captures images and sends them for analysis.

**What it does:**
- Initializes PiCamera2
- Captures high-resolution images (3280x2464)
- Sends images to laptop server via HTTP
- Displays analysis results in terminal
- Handles camera cleanup

**How to use:**
```bash
python pi_camera_capture.py
```

**Configuration needed:**
- **IMPORTANT:** Edit line 145 in the file:
  ```python
  LAPTOP_IP = "192.168.1.100"  # Change to your laptop's IP address
  ```

**What you'll see:**
- Camera initialization message
- Image capture confirmation
- Connection status
- Detailed analysis results with landing sites and craters

**Requirements:** Must run on Raspberry Pi with PiCamera2 connected

---

#### 3. `terrain_analyzer.py` ⭐ **REQUIRED**
**Purpose:** Core analysis module containing all terrain analysis algorithms.

**What it does:**
- Preprocesses images (grayscale conversion, noise reduction)
- Finds flat landing areas using gradient analysis
- Detects craters using Hough Circle Transform and contour detection
- Calculates landing site scores (flatness + terrain proximity)
- Generates navigation instructions (direction and distance)

**Key Functions:**
- `preprocess_image()` - Image preprocessing
- `find_flat_areas()` - Detect flat regions
- `find_craters()` - Detect circular craters
- `select_best_landing_site()` - Choose optimal landing location
- `calculate_navigation()` - Generate navigation instructions

**How to use:** 
- Imported by `laptop_analyzer.py` automatically
- Can be imported in other scripts: `from terrain_analyzer import TerrainAnalyzer`

**Tunable Parameters:**
- `min_size` - Minimum flat area size (default: 100 pixels)
- `min_radius` - Minimum crater radius (default: 15-20 pixels)
- `max_radius` - Maximum crater radius (default: 150-200 pixels)

---

#### 4. `visualize_results.py` ⭐ **OPTIONAL**
**Purpose:** Standalone script to create annotated visualizations of analysis results.

**Runs on:** **Laptop only** (uses OpenCV and `terrain_analyzer`; Pi does not have these dependencies.)

**What it does:**
- Loads an image and its analysis results
- Draws landing sites (green circles)
- Draws craters (red circles)
- Draws navigation lines between landing site and craters
- Saves annotated image

**How to use:**
```bash
# Basic usage
python visualize_results.py image.jpg results.json

# With custom output
python visualize_results.py image.jpg results.json output.jpg

# Auto-find results (if in received_images/)
python visualize_results.py received_images/capture_20240101_120000.jpg
```

**Requirements:** Requires both image file and JSON results file

---

### Configuration Files

#### 5. `requirements.txt` ⭐ **REQUIRED**
**Purpose:** Python dependencies for the laptop/server side.

**Contains:**
- opencv-python (image processing)
- numpy (numerical operations)
- scipy (scientific computing)
- flask (web server)
- flask-cors (cross-origin requests)
- requests (HTTP client)
- pillow (image handling)

**How to use:**
```bash
pip install -r requirements.txt
```

**When to use:** Install on laptop/server before running `laptop_analyzer.py`

---

#### 6. `requirements-pi.txt` ⭐ **REQUIRED**
**Purpose:** Python dependencies for Raspberry Pi.

**Contains:**
- picamera2 (Raspberry Pi camera interface)
- requests (HTTP client for sending images)
- pillow (image handling)

**How to use:**
```bash
pip install -r requirements-pi.txt
```

**When to use:** Install on Raspberry Pi before running `pi_camera_capture.py`

---

#### 7. `pyproject.toml` ⭐ **OPTIONAL**
**Purpose:** Poetry configuration file for dependency management.

**What it does:**
- Defines project metadata
- Lists all dependencies with version constraints
- Used by Poetry package manager

**How to use:**
```bash
# If using Poetry
poetry install
```

**When to use:** Only if you prefer Poetry over pip. Otherwise, use `requirements.txt`

---

#### 8. `poetry.lock` ⭐ **OPTIONAL**
**Purpose:** Poetry lock file ensuring reproducible builds.

**What it does:**
- Locks exact versions of all dependencies
- Ensures consistent installs across environments

**How to use:** Automatically used by Poetry when running `poetry install`

**When to use:** Only if using Poetry. Can be regenerated if deleted.

---

### Documentation Files

#### 9. `README.md` ⭐ **RECOMMENDED**
**Purpose:** Main project documentation.

**Contains:**
- Project overview
- Mission description
- Hardware requirements
- Software setup instructions
- Usage examples
- Troubleshooting guide
- Algorithm explanations

**How to use:** Read for comprehensive project information

---

#### 10. `QUICK_START.md` ⭐ **RECOMMENDED**
**Purpose:** Quick reference guide for getting started.

**Contains:**
- Step-by-step setup instructions
- Running instructions
- Example outputs
- Common troubleshooting

**How to use:** Follow for quick setup and first run

---

### Helper Scripts

#### 11. `run_laptop_server.sh` ⭐ **OPTIONAL**
**Purpose:** Shell script to easily start the laptop server (Mac/Linux).

**What it does:**
- Runs `laptop_analyzer.py` with Python 3
- Provides user-friendly messages

**How to use:**
```bash
# Make executable (first time only)
chmod +x run_laptop_server.sh

# Run
./run_laptop_server.sh
```

**Requirements:** Mac or Linux system

---

#### 12. `run_pi_capture.sh` ⭐ **OPTIONAL**
**Purpose:** Shell script to easily run the Pi camera capture (Mac/Linux).

**What it does:**
- Runs `pi_camera_capture.py` with Python 3
- Provides user-friendly messages

**How to use:**
```bash
# Make executable (first time only)
chmod +x run_pi_capture.sh

# Run
./run_pi_capture.sh
```

**Requirements:** Mac or Linux system (or Raspberry Pi OS)

---

#### 13. `run_laptop_server.bat` ⭐ **OPTIONAL**
**Purpose:** Windows batch script to easily start the laptop server.

**What it does:**
- Runs `laptop_analyzer.py` with Python
- Pauses window after execution

**How to use:**
```bash
# Double-click the file, or:
run_laptop_server.bat
```

**Requirements:** Windows system

---

### Version Control Files

#### 14. `.gitignore` ⭐ **RECOMMENDED**
**Purpose:** Tells Git which files to ignore.

**What it ignores:**
- Virtual environments (`.venv/`)
- IDE settings (`.idea/`)
- Generated images
- Python cache files
- OS files

**How to use:** Automatically used by Git. No manual action needed.

---

## 🚀 Complete Setup Instructions

### Step 1: Initial Setup

#### On Your Laptop:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if using Poetry:
   ```bash
   poetry install
   ```

2. **Find your laptop's IP address:**
   - **Mac/Linux:** Run `ifconfig` or `ip addr`
   - **Windows:** Run `ipconfig`
   - Look for something like `192.168.1.100` or `10.0.0.5`
   - **Write this down!** You'll need it for the Pi.

#### On Raspberry Pi:

1. **Enable the camera:**
   ```bash
   sudo raspi-config
   ```
   Navigate to: Interface Options → Camera → Enable

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements-pi.txt
   ```

3. **Configure the laptop IP address:**
   - Open `pi_camera_capture.py`
   - Find line 145: `LAPTOP_IP = "192.168.1.100"`
   - Change to your laptop's IP address from Step 1

4. **Test camera:**
   ```bash
   libcamera-hello
   ```
   If camera works, you'll see a preview window.

---

### Step 2: Running the System

#### Option A: Using Helper Scripts (Easiest)

**On Laptop:**
```bash
# Mac/Linux
./run_laptop_server.sh

# Windows
run_laptop_server.bat
```

**On Raspberry Pi:**
```bash
./run_pi_capture.sh
```

#### Option B: Using Python Directly

**On Laptop:**
```bash
python laptop_analyzer.py
```

**On Raspberry Pi:**
```bash
python pi_camera_capture.py
```

---

### Step 3: What Happens

1. **Laptop server starts:**
   - Prints startup messages
   - Waits for connections on port 5000
   - Shows: `Running on http://0.0.0.0:5000`

2. **Pi captures image:**
   - Camera initializes
   - Image captured (saved as `terrain_capture.jpg`)
   - Image sent to laptop

3. **Laptop analyzes:**
   - Receives image
   - Finds flat landing areas
   - Detects craters
   - Calculates navigation instructions
   - Returns JSON results

4. **Pi displays results:**
   - Shows landing site location and scores
   - Lists all detected craters
   - Displays navigation instructions

---

## 📊 Understanding the Output

### Landing Site Information:
- **Location:** Pixel coordinates (x, y)
- **Flatness Score:** 0.0-1.0 (higher = flatter)
- **Terrain Proximity:** 0.0-1.0 (higher = closer to terrain features)

### Crater Information:
- **Location:** Pixel coordinates (x, y)
- **Radius:** Size in pixels
- **Distance from Landing Site:** Distance in pixels
- **Direction:** Cardinal direction (N, NE, E, SE, S, SW, W, NW)

### Navigation Instructions:
- **Format:** "Head [DIRECTION] for [DISTANCE] pixels ([ANGLE]° from North)"
- **Example:** "Head NE for 523.5 pixels (45.0° from North)"

### When no landing area is found
- The Pi will show: **"No suitable landing area detected"** plus a short message and tips.
- The server still returns craters (if any). Navigation instructions are omitted because there is no reference landing site.
- **What to do:** Improve lighting, point at flatter terrain, or on the laptop lower `min_size` in `laptop_analyzer.py` so smaller flat regions count as candidates.

### When multiple landing candidates exist
- The analyzer **always picks a single best site** using flatness (60%) and terrain proximity (40%).
- The Pi will show **"Best Landing Site Found (chose best of N candidate areas)"** when N > 1.
- You do not need to choose manually; the best candidate is chosen for you.

---

## 🌙 Accuracy and Homemade Moon Simulation

**This project is designed for a homemade simulation of the moon**, not for real lunar missions. Keep these points in mind:

### What “accuracy” means here
- **Landing sites:** The code finds *flat-looking* regions in the image (low gradient). Accuracy depends on how moon-like your surface is (texture, lighting, contrast). It is **not** calibrated to real lunar terrain.
- **Craters:** Detection uses circles and dark centers. It works best when craters look roughly circular and darker than the surroundings. Real moon craters vary a lot in shape and brightness; a homemade setup may over- or under-detect.
- **Distances and directions:** Reported in **pixels** and **image angles**, not real-world meters or compass degrees. Use them for relative “where to go next” in the simulation, not for physical navigation.

### Why results vary
- **Lighting:** Strong shadows or uneven light change gradients and can hide flat areas or create false ones.
- **Surface:** Smooth, uniform surfaces may yield few “flat” regions; very busy textures may trigger many candidates or none, depending on parameters.
- **Camera and scale:** Resolution and distance to the surface change pixel sizes and how many craters are detected. Parameters like `min_radius` / `max_radius` and `min_size` are in pixels, so they are setup-specific.

### Recommended use
- Treat this as an **educational / simulation tool**: good for learning terrain analysis, not for mission-critical decisions.
- Tune **lighting and surface** for your homemade moon so that flat areas and craters are visible and not overly cluttered.
- Adjust **parameters** (`min_size`, `min_radius`, `max_radius`) to match your setup and surface; document what works for your simulation so you can reuse it.

---

## 🔧 Advanced Usage

### Running Multiple Captures

You can run `pi_camera_capture.py` multiple times:
- Each run captures a new image
- Each image is analyzed independently
- Previous images are saved in `received_images/` directory

### Creating Visualizations

After capturing and analyzing:
```bash
python visualize_results.py received_images/capture_20240101_120000.jpg
```

This creates an annotated image showing:
- Landing site (green circle)
- Craters (red circles)
- Navigation lines (yellow)

### Adjusting Detection Parameters

Edit `terrain_analyzer.py` or `laptop_analyzer.py`:

**In `laptop_analyzer.py` (line 59):**
```python
flat_areas = analyzer.find_flat_areas(processed, min_size=100)  # Change 100
```

**In `laptop_analyzer.py` (line 67):**
```python
craters = analyzer.find_craters(processed, min_radius=15, max_radius=150)  # Adjust radii
```

---

## 🐛 Troubleshooting

### "Could not connect to laptop"
- ✅ Make sure laptop server is running
- ✅ Check IP address in `pi_camera_capture.py` is correct
- ✅ Verify both devices on same network
- ✅ Test connection: `ping <laptop-ip>` from Pi
- ✅ Check firewall allows port 5000

### "Camera not found" or camera errors
- ✅ Enable camera: `sudo raspi-config` → Interface Options → Camera
- ✅ Check camera connection
- ✅ Test camera: `libcamera-hello`
- ✅ Restart Pi if needed

### "No suitable landing area detected"
- ✅ The system now shows this message and tips when no flat area meets the criteria.
- ✅ Ensure image is clear and well-lit; point camera at flatter parts of your moon surface.
- ✅ Try adjusting `min_size` in `laptop_analyzer.py` (e.g. from 100 to 50) so smaller flat regions count.
- ✅ Check image quality and lighting; avoid very dark or overexposed images.

### "No craters detected"
- ✅ Try adjusting `min_radius` and `max_radius` parameters
- ✅ Ensure image has visible circular features
- ✅ Check image contrast and lighting

### Server won't start
- ✅ Check port 5000 is not in use: `lsof -i :5000` (Mac/Linux)
- ✅ Try different port (edit `laptop_analyzer.py` line 173)
- ✅ Check firewall settings
- ✅ Use `python3` instead of `python`

### Import errors
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check Python version (needs 3.8+)
- ✅ Verify virtual environment is activated

---

## 📝 File Dependencies

```
laptop_analyzer.py
  └── imports: terrain_analyzer.py
  └── uses: requirements.txt (dependencies)

pi_camera_capture.py
  └── uses: requirements-pi.txt (dependencies)
  └── connects to: laptop_analyzer.py (via HTTP)

visualize_results.py
  └── imports: terrain_analyzer.py
  └── uses: image files + JSON results

terrain_analyzer.py
  └── standalone module (no dependencies on other project files)
```

---

## 🎯 Quick Reference

### Essential Files (Must Have):
1. `laptop_analyzer.py` - Server script
2. `pi_camera_capture.py` - Pi capture script
3. `terrain_analyzer.py` - Analysis module
4. `requirements.txt` - Laptop dependencies
5. `requirements-pi.txt` - Pi dependencies

### Optional but Useful:
- `visualize_results.py` - Visualization tool
- `run_*.sh` / `run_*.bat` - Helper scripts
- `README.md` / `QUICK_START.md` - Documentation
- `pyproject.toml` / `poetry.lock` - Poetry config (if using Poetry)

### Can Delete:
- `.venv/` - Virtual environment (recreate with `python -m venv .venv`)
- `.idea/` - IDE settings (personal preference)

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Check `QUICK_START.md` for quick setup
3. Review error messages carefully
4. Verify all dependencies are installed
5. Ensure network connectivity between devices
6. Test camera separately with `libcamera-hello`

---

## 🎓 Learning More

- **OpenCV Documentation:** https://docs.opencv.org/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **PiCamera2 Documentation:** https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf

---

**Last Updated:** February 2026
**Project:** CubeSat Terrain Analysis Mission
