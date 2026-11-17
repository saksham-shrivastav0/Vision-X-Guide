import cv2
import numpy as np


def analyze_path_frame(frame):
    """
    Experimental visual probe.

    Highlights candidate edges in the lower image region.
    It does NOT identify a safe path, road, or footpath.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid camera frame")

    output = frame.copy()
    height, width = frame.shape[:2]

    # Focus on the lower part of the image for initial testing.
    y_start = int(height * 0.55)
    roi = frame[y_start:, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 60, 150)

    # Mark the analysis region on the original frame.
    cv2.rectangle(
        output,
        (0, y_start),
        (width - 1, height - 1),
        (255, 180, 0),
        2,
    )

    # Draw detected edge pixels in a separate overlay.
    edge_overlay = np.zeros_like(output)
    edge_overlay[y_start:, :, 1] = edges

    output = cv2.addWeighted(output, 1.0, edge_overlay, 0.8, 0)

    cv2.putText(
        output,
        "EXPERIMENTAL EDGE VIEW - NOT SAFE-PATH DETECTION",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
    )

    return output, edges
