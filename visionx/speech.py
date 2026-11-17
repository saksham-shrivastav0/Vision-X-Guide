import asyncio
import os
import queue
import re
import tempfile
import threading
import time

import edge_tts
import pygame

# --------------------------------------------------
# VISIONX GUIDE - BALANCED HINGLISH VOICE
# --------------------------------------------------

VOICE = "hi-IN-SwaraNeural"
SPEECH_RATE = "-5%"

# Funny lines are occasional and never follow a safety alert.
FUNNY_LINE_COOLDOWN = 120  # seconds

OBJECT_NAMES = {
    "person": "vyakti",
    "car": "car",
    "bus": "bus",
    "truck": "truck",
    "motorcycle": "motorcycle",
    "bicycle": "cycle",
    "chair": "chair",
    "bench": "bench",
    "dog": "dog",
    "cat": "billi",
    "bottle": "bottle",
    "backpack": "bag",
    "handbag": "handbag",
    "suitcase": "suitcase",
    "cell phone": "mobile phone",
    "cellphone": "mobile phone",
    "traffic light": "traffic signal",
    "stop sign": "stop sign",
    "stairs": "seedhiyaan",
    "potted plant": "gamla",
    "motorbike": "motorcycle",
    "train": "train",
    "truck": "truck",
    "fire hydrant": "fire hydrant",
}

FIXED_MESSAGES = {
    "visionx guide started.": "VisionX Guide shuru ho gaya hai.",
    "visionx guide started": "VisionX Guide shuru ho gaya hai.",
    "visionx guide is ready.": "VisionX Guide taiyaar hai.",
    "alerts resumed. alerts phir se chalu hain.": "Alerts phir se chalu hain.",
    "alerts are already active.": "Alerts pehle se chalu hain.",
    "nonessential alerts paused. say resume to continue.": "Non-essential alerts pause hain. Dobara shuru karne ke liye resume boliye.",
    "stopping visionx guide.": "VisionX Guide band ho raha hai.",
    "microphone is not available.": "Microphone available nahi hai.",
    "you can say repeat, pause, resume, or stop assistant. aap repeat, pause, resume, ya band karo bol sakte hain.": "Aap repeat, pause, resume ya assistant band karne ke liye bol sakte hain.",
}


def _to_hinglish(message):
    """Convert common VisionX alerts into natural, concise Hinglish."""

    original = str(message).strip()
    text = original.lower().strip().rstrip(".!?")

    if not text:
        return ""

    if text in FIXED_MESSAGES:
        return FIXED_MESSAGES[text]

    # Directional object alerts from AlertManager.
    patterns = [
        (
            r"(.+?) detected on your left",
            "left",
        ),
        (
            r"(.+?) detected on your right",
            "right",
        ),
        (
            r"(.+?) detected on the left",
            "left",
        ),
        (
            r"(.+?) detected on the right",
            "right",
        ),
        (
            r"(.+?) detected ahead in the camera view",
            "ahead",
        ),
        (
            r"(.+?) detected ahead",
            "ahead",
        ),
    ]

    for pattern, position in patterns:
        match = re.fullmatch(pattern, text)

        if match:
            object_label = match.group(1).strip()
            object_name = OBJECT_NAMES.get(
                object_label,
                object_label,
            )

            # Keep vehicle warnings concise and direct.
            if object_label in {
                "car",
                "bus",
                "truck",
                "motorcycle",
                "motorbike",
            }:
                if position == "left":
                    return f"Baayein taraf {object_name} hai, sambhal kar."
                if position == "right":
                    return f"Daayein taraf {object_name} hai, sambhal kar."
                return f"Saamne camera view mein {object_name} hai, dhyan dein."

            if position == "left":
                return f"Baayein taraf {object_name} hai, dhyan dein."
            if position == "right":
                return f"Daayein taraf {object_name} hai, dhyan dein."
            return f"Saamne camera view mein {object_name} hai."

    # Alternative message formats from different alert versions.
    match = re.fullmatch(r"(.+?) detected on the left", text)
    if match:
        return f"Baayein taraf {match.group(1)} hai, dhyan dein."

    match = re.fullmatch(r"(.+?) detected on the right", text)
    if match:
        return f"Daayein taraf {match.group(1)} hai, dhyan dein."

    if "no object" in text:
        return "Abhi camera view mein koi recognised object alert nahi hai."

    # Friendly translations for common controls.
    if text in {"repeat", "repeat last message"}:
        return "Pichhla message dobara sunaiye."

    if text in {"help", "available commands"}:
        return "Aap repeat, pause, resume aur stop assistant bol sakte hain."

    # Don't silently discard an unfamiliar message.
    return original


class SpeechManager:
    def __init__(self, rate=165):
        self.rate = rate
        self.voice = VOICE

        self._queue = queue.Queue()
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self._started = False
        self._stopped = False

        self._speaking = threading.Event()
        self._last_message = None
        self._last_safety_alert_time = 0.0
        self._last_funny_line_time = 0.0

        self._funny_lines = [
            "VisionX duty par hai, chaliye smartly.",
            "Technology apna kaam kar rahi hai, aap aaram se suniye.",
            "VisionX saath hai, confidence ke saath aage badhiye.",
        ]

        self._funny_index = 0

    @property
    def is_speaking(self):
        return self._speaking.is_set()

    @property
    def speaking(self):
        return self._speaking.is_set()

    def start(self):
        if not self._started and not self._stopped:
            self._thread.start()
            self._started = True

    def say(self, message):
        if self._stopped:
            return

        message = str(message).strip()
        if not message:
            return

        self.start()
        self._queue.put(message)

    def repeat_last(self):
        if self._last_message:
            self.say(self._last_message)
        else:
            self.say("Abhi repeat karne ke liye koi pichhla message nahi hai.")

    async def _generate_audio(self, message, path):
        communicate = edge_tts.Communicate(
            message,
            self.voice,
            rate=SPEECH_RATE,
        )
        await communicate.save(path)

    def _speak_one(self, message):
        path = None

        try:
            spoken_text = _to_hinglish(message)
            if not spoken_text:
                return

            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False,
            ) as audio_file:
                path = audio_file.name

            asyncio.run(self._generate_audio(spoken_text, path))

            # Preserve the working playback reset between messages.
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    pygame.mixer.quit()
            except pygame.error:
                pass

            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self._stopped:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.05)

            self._last_message = message

        except Exception as error:
            print(f"Voice error: {error}")

        finally:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    pygame.mixer.quit()
            except pygame.error:
                pass

            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _is_safety_alert(self, message):
        text = str(message).lower()

        return (
            "detected on your left" in text
            or "detected on your right" in text
            or "detected on the left" in text
            or "detected on the right" in text
            or "detected ahead" in text
        )

    def _maybe_say_funny_line(self, previous_message):
        # Never insert a joke immediately after a detected-object alert.
        if self._is_safety_alert(previous_message):
            self._last_safety_alert_time = time.monotonic()
            return

        now = time.monotonic()

        # Keep the jokes rare, and only speak one when the queue is empty.
        if not self._queue.empty():
            return

        if now - self._last_funny_line_time < FUNNY_LINE_COOLDOWN:
            return

        # A joke is only eligible after a non-alert message.
        # It does not indicate that the surroundings are safe.
        joke = self._funny_lines[self._funny_index % len(self._funny_lines)]
        self._funny_index += 1
        self._last_funny_line_time = now

        self._speak_one(joke)

    def _worker(self):
        while True:
            message = self._queue.get()

            try:
                if message is None:
                    return

                self._speaking.set()
                self._speak_one(message)

                # Give queued alerts priority over friendly lines.
                self._maybe_say_funny_line(message)

            finally:
                self._speaking.clear()
                self._queue.task_done()

    def stop(self):
        if self._stopped:
            return

        self._stopped = True

        if self._started and self._thread.is_alive():
            self._queue.put(None)
            self._thread.join(timeout=30)
