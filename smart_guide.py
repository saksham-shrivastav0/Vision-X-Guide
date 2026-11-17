import cv2
import time
import threading
import speech_recognition as sr

from ultralytics import YOLO
from visionx.alerts import AlertManager
from visionx.speech import SpeechManager
from visionx.voice_commands import VoiceCommandHandler

MODEL_PATH = "yolo11n.pt"
CAMERA_INDEX = 2
CONFIDENCE = 0.70


def get_position(center_x, frame_width):
    if center_x < frame_width / 3:
        return "on the left"
    elif center_x > 2 * frame_width / 3:
        return "on the right"
    return "near the center of the camera view"


def get_area_ratio(x1, y1, x2, y2, frame_width, frame_height):
    box_width = max(0.0, x2 - x1)
    box_height = max(0.0, y2 - y1)
    frame_area = max(1, frame_width * frame_height)
    return (box_width * box_height) / frame_area


def microphone_worker(speech, commands, exit_event):
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    print("[VOICE] Initializing microphone...")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VOICE] Ready. Say Help, Repeat, Pause, or Resume.")

            while not exit_event.is_set():

                # Avoid listening while the assistant is speaking.
                if speech.is_speaking:
                    time.sleep(0.1)
                    continue

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=2,
                        phrase_time_limit=4,
                    )

                    # Discard audio captured while TTS was speaking.
                    if speech.is_speaking:
                        continue

                    text = None

                    for language in ("en-IN", "hi-IN"):
                        try:
                            text = recognizer.recognize_google(
                                audio,
                                language=language,
                            )
                            break
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as error:
                            print(f"[VOICE NETWORK ERROR] {error}")
                            break

                    if text:
                        print(f"[VOICE HEARD] {text}")
                        commands.handle(text)

                except sr.WaitTimeoutError:
                    continue

    except OSError as error:
        print(f"[MICROPHONE ERROR] {error}")
        speech.say("Microphone unavailable. Use the keyboard to control VisionX Guide.")

    except Exception as error:
        print(f"[VOICE ERROR] {error}")


def main():
    print("Loading VisionX Guide...")

    model = YOLO(MODEL_PATH)

    alerts = AlertManager(
        cooldown=3.0,
        forget_after=2.0,
        min_confidence=CONFIDENCE,
    )

    speech = SpeechManager(rate=155)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    exit_event = threading.Event()

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    commands = VoiceCommandHandler(
        speech=speech,
        on_exit=exit_event.set,
    )

    voice_thread = None

    try:
        speech.start()

        voice_thread = threading.Thread(
            target=microphone_worker,
            args=(speech, commands, exit_event),
            name="VisionX-Microphone",
            daemon=True,
        )
        voice_thread.start()

        speech.say("VisionX Guide started. Say Help for voice commands.")

        print("VisionX Guide is running.")
        print("Voice commands: Help, Repeat, Pause, Resume, Stop assistant.")
        print("Keyboard backup: H = Help, R = Repeat, P = Pause/Resume, Q = Quit.")

        while not exit_event.is_set():

            success, frame = camera.read()

            if not success:
                print("Could not read webcam frame.")
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            results = model.predict(
                frame,
                imgsz=640,
                conf=CONFIDENCE,
                verbose=False,
            )

            result = results[0]
            display = result.plot()
            detections = []

            if result.boxes is not None:
                for box in result.boxes:
                    confidence = float(box.conf[0].item())
                    class_id = int(box.cls[0].item())
                    name = model.names[class_id]

                    x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()
                    center_x = (x1 + x2) / 2

                    position = get_position(center_x, width)

                    area_ratio = get_area_ratio(x1, y1, x2, y2, width, height)

                    detections.append(
                        {
                            "name": name,
                            "position": position,
                            "confidence": confidence,
                            "area_ratio": area_ratio,
                        }
                    )

            detections.sort(
                key=lambda item: (
                    item["area_ratio"],
                    item["confidence"],
                ),
                reverse=True,
            )

            # While paused, suppress ordinary object announcements.
            if not commands.paused:
                message = alerts.choose_alert(detections)

                if message:
                    print("Voice alert:", message)
                    speech.say(message)

            priority = alerts.current_priority

            if priority is not None:
                status = f"Priority: {priority['name']} " f"| {priority['position']}"

                cv2.putText(
                    display,
                    status,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2,
                )

            cv2.putText(
                display,
                "VisionX Guide - Voice Assistant",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
            )

            cv2.imshow("VisionX Guide", display)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                print("Exit requested.")
                exit_event.set()
                break

            elif key == ord("h"):
                commands.handle("help")

            elif key == ord("r"):
                commands.handle("repeat")

            elif key == ord("p"):
                if commands.paused:
                    commands.handle("resume")
                else:
                    commands.handle("pause")

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")

    finally:
        exit_event.set()
        camera.release()
        cv2.destroyAllWindows()

        # Allow the microphone thread to finish its current operation.
        if voice_thread is not None:
            voice_thread.join(timeout=2)

        speech.stop()
        print("VisionX Guide stopped.")


if __name__ == "__main__":
    main()
