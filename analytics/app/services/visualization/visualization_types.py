from enum import Enum

class VisualizationType(str, Enum):
    BAR ="BAR"
    LINE = "LINE"
    SCATTER = "SCATTER"
    HISTOGRAM = "HISTOGRAM"
    BOX_PLOT = "BOX_PLOT"
    PIE = "PIE"
    HEATMAP = "HEATMAP"
    TABLE = "TABLE"
    