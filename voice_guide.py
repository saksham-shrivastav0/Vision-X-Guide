import cv2
import pyttsx3
import queue
import threading
import time
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

# Keep speech separate from camera processing
speech_queue = queue.Queue(maxsize=1)


def speech_worker():
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)

    while True:
        message = speech_queue.get()

        if message is None:
            break

        try:
            engine.say(message)
            engine.runAndWait()
        except Exception as error:
            print("Speech error:", error)

    engine.stop()


def announce(message):
    # Avoid building up a long queue of old announcements
    if speech_queue.empty():
        try:
            speech_queue.put_nowait(message)
        except queue.Full:
            pass


def main():
    threading.Thread(target=speech_worker, daemon=True).start()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open webcam.")
        return

    last_message = ""
    last_seen = 0
    last_announcement = 0

    print("VisionX Guide voice prototype started.")
    print("Press Q to quit.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            results = model.predict(frame, imgsz=416, conf=0.50, verbose=False)

            result = results[0]
            display = result.plot()
            current_message = ""

            if result.boxes is not None:
                boxes = result.boxes

                if len(boxes) > 0:
                    # Select the highest-confidence detection
                    best_index = int(boxes.conf.argmax())
                    box = boxes.xyxy[best_index].cpu().tolist()
                    class_id = int(boxes.cls[best_index].item())

                    x1, y1, x2, y2 = box
                    object_name = model.names[class_id]

                    center_x = (x1 + x2) / 2

                    if center_x < width / 3:
                        position = "on your left"
                    elif center_x > 2 * width / 3:
                        position = "on your right"
                    else:
                        position = "ahead in the camera view"

                    current_message = f"{object_name} {position}"

            now = time.time()

            if current_message:
                last_seen = now

                # Speak only when the detected description changes.
                # Apply a cooldown to avoid rapid announcements.
                if current_message != last_message and now - last_announcement >= 3:
                    announce(current_message)
                    print("Voice alert:", current_message)
                    last_message = current_message
                    last_announcement = now

            elif now - last_seen > 2:
                last_message = ""

            cv2.putText(
                display,
                "VisionX Guide - Voice Prototype",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
            )

            cv2.imshow("VisionX Guide", display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("VisionX Guide stopped.")


if __name__ == "__main__":
    main()
