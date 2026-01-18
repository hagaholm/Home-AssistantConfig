# Camera Comparison Analysis

**Generated from**: `config_safe_2026-01-18_13-03-50.yaml`  
**Date**: 2026-01-18 13:03:51



## Complete Camera Configuration Comparison Table

This table shows all Frigate configuration values for each camera, making it easy to see differences:

| Configuration Parameter | Cam3 | Cam5 | Cam6 | Cam7 | Cam8 |
|---|---|---|---|---|---|
| **ENABLED** |
| Camera Enabled | true | true | true | true | true |
| **DETECTION** |
| Detection FPS | 5 | 5 | 5 | 5 | 5 |
| Detection Width | 1280 | 1280 | 1280 | 1280 | 1280 |
| Detection Height | 720 | 720 | 720 | 720 | 720 |
| **DETECTION FILTERS - ALL OBJECTS** |
| Min Area (pixels) | **1000** | **1000** â¬†ï¸ | **1000** â¬‡ï¸ | **1000** | **1000** |
| Min Score | **0.4** | **0.4** | **0.4** | **0.4** | **0.4** |
| Threshold | **0.6** | **0.6** | **0.6** | **0.6** | **0.6** |
| **DETECTION FILTERS - PERSON** |
| Person Max Ratio | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 |
| Person Mask | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes |
| **MOTION DETECTION** |
| Motion Threshold | **30** | **30** | **30** | **30** | **30** |
| Motion Contour Area | **10** | **10** | **10** | **10** | **10** |
| **SNAPSHOTS** |
| Clean Copy | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes | âœ… Yes |
| **ZONES** |
| Zone Name | Uppfarten | Baksidan | Baksidan | Entre | Baksidan |

---

## Key Differences Highlighted

### ðŸ”´ Most Sensitive Settings (Lowest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (smallest) | **Cam6** | 1000 | Rear entrance - needs to catch close-up detections |
| Min Score (lowest) | **Cam6, Cam7, Cam8** | 0.4 | More permissive detection |

### ðŸŸ¢ Least Sensitive Settings (Highest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (largest) | **Cam5** | 1000 | Rear yard - avoids distant noise |
| Min Score (highest) | **Cam3** | 0.4 | More strict detection |

### ðŸ“Š Sensitivity Summary Table

| Camera | Min Area | Min Score | Motion Threshold | Contour Area |
|--------|----------|-----------|------------------|--------------|
| **Cam3** (Driveway) | 1000 | 0.4 | 30 | 10 |
| **Cam5** (Rear Yard) | 1000 | 0.4 | 30 | 10 |
| **Cam6** (Rear Entrance) | 1000 | 0.4 | 30 | 10 |
| **Cam7** (Garden Shed) | 1000 | 0.4 | 30 | 10 |
| **Cam8** (Main Entrance) | 1000 | 0.4 | 30 | 10 |

---

## Configuration Patterns

### Pattern: Where Cameras Differ
âŒ **Min Area**: 1000 vs 1000 vs 1000 vs 1000 vs 1000  
âŒ **Min Score**: 0.4 vs 0.4 vs 0.4 vs 0.4 vs 0.4  
âŒ **Motion Threshold**: 30 vs 30 vs 30 vs 30 vs 30  
âŒ **Motion Contour Area**: 10 vs 10 vs 10 vs 10 vs 10  
âŒ **Clean Copy**: Cam3 only = true  
âŒ **Person Mask**: Cam3 = true, Cam8 = true

---

**Source File**: `config_safe_2026-01-18_13-03-50.yaml`  
**Generated**: 2026-01-18 13:03:51
