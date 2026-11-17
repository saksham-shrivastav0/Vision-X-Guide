from visionx.speech import SpeechManager
import time


def main():
    speech = SpeechManager()
    speech.start()

    try:
        speech.say("VisionX Guide started. Say Help for voice commands.")

        speech.say("Vehicle detected on the left")

        speech.say("person detected on your right")

        speech.say("chair detected ahead in the camera view")

        # Wait for all queued speech to finish.
        speech.messages.join()

        print("Hinglish speech test completed.")

    except KeyboardInterrupt:
        print("Test interrupted.")

    finally:
        speech.stop()


if __name__ == "__main__":
    main()
