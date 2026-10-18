# Camera Comparison Analysis

**Generated from**: `config_safe_2026-06-29_21-48-34.yaml`  
**Date**: 2026-10-18 18:38:15



## Complete Camera Configuration Comparison Table

This table shows all Frigate configuration values for each camera, making it easy to see differences:

| Configuration Parameter | Cam5 | Cam6 | Cam8 | Cam9 | Cam10 |
|---|---|---|---|---|---|
| **ENABLED** |
| Camera Enabled | true | true | true | true | true |
| **DETECTION** |
| Detection FPS | 5 | 5 | 5 | 5 | 5 |
| Detection Width | 1280 | 1280 | 1280 | 1280 | 1280 |
| Detection Height | 720 | 720 | 720 | 720 | 720 |
| **DETECTION FILTERS - ALL OBJECTS** |
| Min Area (pixels) | **3000** | **3000** â¬†ï¸ | **1500** â¬‡ï¸ | **1500** | **1500** |
| Min Score | **0.75** | **0.75** | **0.5** | **0.4** | **0.4** |
| Threshold | **0.8** | **0.8** | **0.65** | **0.62** | **0.62** |
| **DETECTION FILTERS - PERSON** |
| Person Max Ratio | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 |
| Person Mask | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes |
| **MOTION DETECTION** |
| Motion Threshold | **38** | **38** | **38** | **38** | **38** |
| Motion Contour Area | **10** | **10** | **10** | **10** | **10** |
| **SNAPSHOTS** |
| Clean Copy | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes |
| **ZONES** |
| Zone Name | Baksidan | Baksidan | Baksidan | uppfarten | Uppfarten |

---

## Key Differences Highlighted

### ðŸ”´ Most Sensitive Settings (Lowest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (smallest) | **Cam6** | 3000 | Rear entrance - needs to catch close-up detections |
| Min Score (lowest) | **Cam6, Cam8, Cam9** | 0.75 | More permissive detection |

### ðŸŸ¢ Least Sensitive Settings (Highest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (largest) | **Cam5** | 3000 | Rear yard - avoids distant noise |
| Min Score (highest) | **Cam10** | 0.4 | More strict detection |

### ðŸ“Š Sensitivity Summary Table

| Camera | Min Area | Min Score | Motion Threshold | Contour Area |
|--------|----------|-----------|------------------|--------------|
| **Cam5** (Rear Yard) | 3000 | 0.75 | 38 | 10 |
| **Cam6** (Rear Entrance) | 3000 | 0.75 | 38 | 10 |
| **Cam8** (Main Entrance) | 1500 | 0.5 | 38 | 10 |
| **Cam9** (Garden Shed) | 1500 | 0.4 | 38 | 10 |
| **Cam10** (Driveway) | 1500 | 0.4 | 38 | 10 |

---

## Configuration Patterns

### Pattern: Where Cameras Differ
âŒ **Min Area**: 3000 vs 3000 vs 1500 vs 1500 vs 1500  
âŒ **Min Score**: 0.75 vs 0.75 vs 0.5 vs 0.4 vs 0.4  
âŒ **Motion Threshold**: 38 vs 38 vs 38 vs 38 vs 38  
âŒ **Motion Contour Area**: 10 vs 10 vs 10 vs 10 vs 10  
âŒ **Clean Copy**: Cam5, Cam6, Cam8, Cam9, Cam10 = true / true / true / true / true  
âŒ **Person Mask**: Cam5, Cam6, Cam8, Cam9, Cam10 = true / true / true / true / true

---

**Source File**: `config_safe_2026-06-29_21-48-34.yaml`  
**Generated**: 2026-10-18 18:38:15
