
import cv2
from ultralytics import YOLO

# Load a small pretrained object detection model
model = YOLO("yolo11n.pt")

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    print("VisionX Guide: AI detection started!")
    print("Press Q to quit.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read camera frame.")
                break

            frame = cv2.flip(frame, 1)

            # Run AI object detection
            results = model.predict(
                source=frame,
                imgsz=416,
                conf=0.45,
                verbose=False
            )

            # Draw boxes and object labels
            annotated_frame = results[0].plot()

            cv2.putText(
                annotated_frame,
                "VisionX Guide - AI Detection",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("VisionX Guide", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
