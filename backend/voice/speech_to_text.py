import os
import tempfile
import wave

import sounddevice as sd
from faster_whisper import WhisperModel


class SpeechToText:

    def __init__(
        self,
        model_size="base.en",
        device="cpu",
        compute_type="int8",
        sample_rate=16000,
        channels=1,
        microphone_device=1
    ):

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        self.sample_rate = sample_rate
        self.channels = channels

        self.microphone_device = (
            microphone_device
        )

        self.model = None

    # ==========================================
    # MODEL
    # ==========================================

    def load_model(self):

        if self.model is not None:
            return

        print(
            f"AEGIS: Loading Whisper "
            f"model '{self.model_size}'..."
        )

        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )

        print(
            "AEGIS: Speech recognition ready."
        )

    # ==========================================
    # RECORD
    # ==========================================

    def record(
        self,
        duration=5
    ):

        if duration <= 0:
            raise ValueError(
                "Recording duration must be positive."
            )

        print(
            f"AEGIS: Listening for "
            f"{duration} seconds..."
        )

        audio = sd.rec(
            int(
                duration
                * self.sample_rate
            ),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            device=self.microphone_device
        )

        sd.wait()

        return audio

    # ==========================================
    # SAVE WAV
    # ==========================================

    def _save_wav(
        self,
        audio,
        path
    ):

        with wave.open(
            path,
            "wb"
        ) as wav_file:

            wav_file.setnchannels(
                self.channels
            )

            wav_file.setsampwidth(
                2
            )

            wav_file.setframerate(
                self.sample_rate
            )

            wav_file.writeframes(
                audio.tobytes()
            )

    # ==========================================
    # TRANSCRIBE
    # ==========================================

    def transcribe_file(
        self,
        path
    ):

        self.load_model()

        segments, info = (
            self.model.transcribe(
                path,
                beam_size=5,
                language="en",
                vad_filter=True
            )
        )

        text_parts = []

        for segment in segments:

            text = segment.text.strip()

            if text:
                text_parts.append(
                    text
                )

        text = " ".join(
            text_parts
        ).strip()

        return {
            "text": text,
            "language": info.language,
            "language_probability": (
                info.language_probability
            )
        }

    # ==========================================
    # LISTEN
    # ==========================================

    def listen(
        self,
        duration=5
    ):

        audio = self.record(
            duration
        )

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as temp_file:

                temp_path = temp_file.name

            self._save_wav(
                audio,
                temp_path
            )

            return self.transcribe_file(
                temp_path
            )

        finally:

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                try:
                    os.remove(
                        temp_path
                    )
                except OSError:
                    pass

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.model = None


if __name__ == "__main__":

    speech = SpeechToText()

    try:

        result = speech.listen(
            duration=5
        )

        print(
            "\nTRANSCRIPTION:"
        )

        print(
            result
        )

    finally:

        speech.close()