class VoiceCommandHandler:
    def __init__(self, speech, on_exit=None):
        self.speech = speech
        self.on_exit = on_exit
        self.paused = False

    def handle(self, text):
        if not text:
            return False

        command = text.lower().strip()
        command = command.replace(".", "").replace(",", "")

        # HELP
        if any(
            word in command
            for word in [
                "help",
                "madad",
                "commands",
                "kya kar sakte",
            ]
        ):
            self.speech.say(
                "You can say repeat, pause, resume, or stop assistant. "
                "Aap repeat, pause, resume, ya band karo bol sakte hain."
            )
            return True

        # REPEAT LAST SPOKEN ALERT
        if any(
            word in command
            for word in [
                "repeat",
                "dobara bolo",
                "phir se bolo",
                "repeat karo",
            ]
        ):
            self.speech.repeat_last()
            return True

        # RESUME must be checked before pause.
        if any(
            word in command
            for word in [
                "resume",
                "shuru karo",
                "alerts chalu",
                "wapas chalu",
            ]
        ):
            if self.paused:
                self.paused = False
                self.speech.say("Alerts resumed. Alerts phir se chalu hain.")
            else:
                self.speech.say("Alerts are already active.")
            return True

        # PAUSE
        if any(
            word in command
            for word in [
                "pause",
                "ruko",
                "alerts band",
                "shant ho jao",
            ]
        ):
            self.paused = True
            self.speech.say("Nonessential alerts paused. Say resume to continue.")
            return True

        # STOP ASSISTANT
        if any(
            phrase in command
            for phrase in [
                "stop assistant",
                "exit assistant",
                "band karo",
                "program band",
            ]
        ):
            self.speech.say("Stopping VisionX Guide.")
            if self.on_exit:
                self.on_exit()
            return True

        return False
