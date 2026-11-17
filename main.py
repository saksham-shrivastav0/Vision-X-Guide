
import cv2

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        camera.release()
        return

    print("VisionX Guide camera started!")
    print("Press Q to quit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Error: Could not read camera frame.")
            break

        # Mirror the video like a selfie camera
        frame = cv2.flip(frame, 1)

        # Add the VisionX Guide title
        cv2.putText(
            frame,
            "VisionX Guide - Prototype 1",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("VisionX Guide", frame)

        # Press Q to close the camera window
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("VisionX Guide stopped.")

if __name__ == "__main__":
    main()
