import cv2
from visionx.path_probe import analyze_path_frame

CAMERA_INDEX = 0

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise RuntimeError("Camera open nahi hua. Check iVCam and CAMERA_INDEX.")

try:
    while True:
        ok, frame = cap.read()

        if not ok:
            print("Camera frame read failed.")
            break

        preview, edges = analyze_path_frame(frame)

        cv2.imshow("VisionX - Path Probe", preview)
        cv2.imshow("VisionX - Edge Map", edges)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
