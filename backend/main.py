import re

from backend.ai.brain import AegisBrain
from backend.voice.voice_manager import VoiceManager


class AegisApplication:

    def __init__(self):

        self.brain = AegisBrain()

        self.voice = VoiceManager(
            microphone_device=1
        )

        self.voice_mode = False

        self.voice_calibrated = False

    # ==========================================
    # COMMAND NORMALIZATION
    # ==========================================

    @staticmethod
    def normalize_command(
        text
    ):

        text = str(
            text or ""
        ).strip().lower()

        text = re.sub(
            r"[.!?,;:]+$",
            "",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ==========================================
    # KEYBOARD INPUT
    # ==========================================

    def keyboard_input(self):

        try:

            return input(
                "You: "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\nAEGIS: Shutting down. Goodbye."
            )

            return "exit"

    # ==========================================
    # VOICE CONTROL INPUT
    # ==========================================

    def voice_control_input(self):

        try:

            command = input(
                "\nPress ENTER to speak, "
                "or type 'keyboard mode' "
                "or 'exit': "
            ).strip()

        except KeyboardInterrupt:

            return "exit"

        normalized = (
            self.normalize_command(
                command
            )
        )

        if normalized in {
            "keyboard mode",
            "disable voice",
            "turn off voice",
            "switch to keyboard",
            "keyboard"
        }:

            return "keyboard mode"

        if normalized in {
            "exit",
            "quit",
            "shutdown",
            "goodbye"
        }:

            return "exit"

        # Anything else, including empty input,
        # means "start listening".
        return "__listen__"

    # ==========================================
    # VOICE INPUT
    # ==========================================

    def voice_input(self):

        result = self.voice.listen(
            max_duration=8
        )

        if result.get(
            "error"
        ):

            print(
                "AEGIS VOICE ERROR:",
                result["error"]
            )

            return ""

        text = result.get(
            "text",
            ""
        ).strip()

        if text:

            print(
                "You:",
                text
            )

        else:

            print(
                "AEGIS: I didn't hear anything."
            )

        return text

    # ==========================================
    # ENABLE VOICE
    # ==========================================

    def enable_voice(self):

        self.voice_mode = True

        print(
            "AEGIS: Voice mode enabled."
        )

        if not self.voice_calibrated:

            print(
                "AEGIS: Calibrating microphone..."
            )

            calibration = (
                self.voice.calibrate()
            )

            if calibration:

                self.voice_calibrated = True

        self.voice.speak(
            "Voice mode enabled. "
            "Press Enter whenever you want to speak."
        )

    # ==========================================
    # HANDLE COMMAND
    # ==========================================

    def handle_command(
        self,
        user_input
    ):

        normalized = (
            self.normalize_command(
                user_input
            )
        )

        if normalized in {
            "exit",
            "quit",
            "shutdown",
            "goodbye"
        }:

            return False

        # --------------------------------------
        # Voice mode
        # --------------------------------------

        if normalized in {
            "voice mode",
            "enable voice",
            "turn on voice",
            "switch to voice",
            "voice"
        }:

            self.enable_voice()

            return True

        # --------------------------------------
        # Keyboard mode
        # --------------------------------------

        if normalized in {
            "keyboard mode",
            "disable voice",
            "turn off voice",
            "switch to keyboard",
            "keyboard"
        }:

            self.voice_mode = False

            print(
                "AEGIS: Keyboard mode enabled."
            )

            return True

        if not user_input.strip():

            return True

        try:

            answer = self.brain.think(
                user_input
            )

        except Exception as error:

            answer = (
                "I encountered an error: "
                f"{error}"
            )

        print()
        print(
            "AEGIS:",
            answer
        )
        print()

        if self.voice_mode:

            self.voice.speak(
                answer
            )

        return True

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        print("=" * 55)
        print("                PROJECT AEGIS")
        print("                AI Assistant v1.0")
        print("=" * 55)

        print(
            "AEGIS is online."
        )

        print(
            "Keyboard mode is active."
        )

        print(
            "Say/type 'voice mode' to enable voice."
        )

        print(
            "Type 'exit' or 'quit' to shut down."
        )

        print()

        try:

            while True:

                if self.voice_mode:

                    control = (
                        self.voice_control_input()
                    )

                    if control == "exit":

                        print(
                            "\nAEGIS: "
                            "Shutting down. Goodbye."
                        )

                        break

                    if control == "keyboard mode":

                        self.voice_mode = False

                        print(
                            "AEGIS: "
                            "Keyboard mode enabled."
                        )

                        continue

                    if control == "__listen__":

                        user_input = (
                            self.voice_input()
                        )

                    else:

                        user_input = control

                else:

                    user_input = (
                        self.keyboard_input()
                    )

                should_continue = (
                    self.handle_command(
                        user_input
                    )
                )

                if not should_continue:

                    print(
                        "\nAEGIS: "
                        "Shutting down. Goodbye."
                    )

                    break

        finally:

            self.close()

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        try:

            self.voice.close()

        except Exception:
            pass

        try:

            self.brain.close()

        except Exception:
            pass


def main():

    application = AegisApplication()

    application.run()


if __name__ == "__main__":

    main()