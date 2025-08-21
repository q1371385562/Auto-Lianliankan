# coding: utf-8
"""Configuration for Auto-Lianliankan.
All parameters can be hot reloaded at runtime.
"""

# ROI (region of interest) of the board: x, y, width, height
ROI = (0, 0, 0, 0)
# Force re-select ROI on start
ROI_RESET = False
# Save ROI back to this file after selection
SAVE_ROI_BACK_TO_CONFIG = True

# Target detection + clustering parameters
MIN_AREA = 400        # minimum area of a tile
MAX_AREA = 4000       # maximum area of a tile
ASPECT_TOL = 0.3      # allowed aspect ratio difference from square
NMS_DIST = 10         # suppress detections closer than this (pixels)
CROP_RATIO = 0.1      # crop percent from each side before comparison
SSIM_THR = 0.95       # similarity threshold for grouping tiles

# Click parameters
CLICK_OFFSET_X = 0
CLICK_OFFSET_Y = -8   # click above the center to avoid shadow
CLICK_DELAY_MS = 50
LOOP_SLEEP_MS = 200

# Hotkeys
PAUSE_HOTKEY = 'f12'
EXIT_HOTKEY = 'esc'
RELOAD_HOTKEY = 'enter'

# Behaviour
DEBUG = True          # show debug visualization

