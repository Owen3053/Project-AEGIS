import os
import tempfile
import time
import wave

import numpy as np
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
        microphone_device=1,
        chunk_duration=0.2,
        silence_duration=1.0,
        speech_threshold=0.025,
        min_speech_duration=0.4,
        pre_speech_duration=0.4
    ):

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        self.sample_rate = sample_rate
        self.channels = channels

        self.microphone_device = (
            microphone_device
        )

        self.chunk_duration = (
            chunk_duration
        )

        self.silence_duration = (
            silence_duration
        )

        self.speech_threshold = (
            speech_threshold
        )

        self.min_speech_duration = (
            min_speech_duration
        )

        self.pre_speech_duration = (
            pre_speech_duration
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
    # MICROPHONE CALIBRATION
    # ==========================================

    def calibrate(
        self,
        duration=2.0,
        safety_factor=3.0
    ):

        print()
        print(
            "AEGIS: Microphone calibration."
        )

        print(
            "Stay quiet for "
            f"{duration:.1f} seconds..."
        )

        time.sleep(0.5)

        frames = int(
            duration
            * self.sample_rate
        )

        audio = sd.rec(
            frames,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.microphone_device
        )

        sd.wait()

        rms = float(
            np.sqrt(
                np.mean(
                    np.square(audio)
                )
            )
        )

        calculated_threshold = (
            rms * safety_factor
        )

        self.speech_threshold = max(
            0.008,
            min(
                calculated_threshold,
                0.10
            )
        )

        print(
            "AEGIS: Calibration complete."
        )

        print(
            f"AEGIS: Noise level = {rms:.5f}"
        )

        print(
            f"AEGIS: Speech threshold = "
            f"{self.speech_threshold:.5f}"
        )

        return {
            "noise_rms": rms,
            "speech_threshold": (
                self.speech_threshold
            )
        }

    # ==========================================
    # RECORD
    # ==========================================

    def record(
        self,
        max_duration=8
    ):

        if max_duration <= 0:

            raise ValueError(
                "Maximum duration must be positive."
            )

        chunk_frames = int(
            self.chunk_duration
            * self.sample_rate
        )

        max_chunks = int(
            max_duration
            / self.chunk_duration
        )

        required_speech_chunks = max(
            1,
            int(
                self.min_speech_duration
                / self.chunk_duration
            )
        )

        silence_chunks_required = max(
            1,
            int(
                self.silence_duration
                / self.chunk_duration
            )
        )

        pre_speech_chunks = max(
            0,
            int(
                self.pre_speech_duration
                / self.chunk_duration
            )
        )

        chunks = []
        pre_buffer = []

        speech_started = False
        consecutive_speech_chunks = 0
        silent_chunks = 0

        print(
            "AEGIS: Listening..."
        )

        for _ in range(
            max_chunks
        ):

            audio = sd.rec(
                chunk_frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                device=self.microphone_device
            )

            sd.wait()

            audio = audio.copy()

            rms = float(
                np.sqrt(
                    np.mean(
                        np.square(audio)
                    )
                )
            )

            if not speech_started:

                pre_buffer.append(
                    audio
                )

                if len(pre_buffer) > (
                    pre_speech_chunks
                ):

                    pre_buffer.pop(0)

                if rms >= self.speech_threshold:

                    consecutive_speech_chunks += 1

                else:

                    consecutive_speech_chunks = 0

                if (
                    consecutive_speech_chunks
                    >= required_speech_chunks
                ):

                    speech_started = True

                    chunks.extend(
                        pre_buffer
                    )

                    silent_chunks = 0

                continue

            chunks.append(
                audio
            )

            if rms >= self.speech_threshold:

                silent_chunks = 0

            else:

                silent_chunks += 1

                if (
                    silent_chunks
                    >= silence_chunks_required
                ):

                    break

        if not chunks:

            return np.zeros(
                (
                    0,
                    self.channels
                ),
                dtype=np.float32
            )

        return np.concatenate(
            chunks,
            axis=0
        )

    # ==========================================
    # SAVE WAV
    # ==========================================

    def _save_wav(
        self,
        audio,
        path
    ):

        pcm = np.clip(
            audio,
            -1.0,
            1.0
        )

        pcm = (
            pcm * 32767
        ).astype(
            np.int16
        )

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
                pcm.tobytes()
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

        text = (
            self._remove_simple_repetition(
                text
            )
        )

        return {
            "text": text,
            "language": info.language,
            "language_probability": (
                info.language_probability
            )
        }

    # ==========================================
    # REPETITION FILTER
    # ==========================================

    @staticmethod
    def _remove_simple_repetition(
        text
    ):

        words = text.split()

        if len(words) < 4:
            return text

        midpoint = len(words) // 2

        if (
            len(words) % 2 == 0
            and words[:midpoint]
            == words[midpoint:]
        ):

            return " ".join(
                words[:midpoint]
            )

        return text

    # ==========================================
    # LISTEN
    # ==========================================

    def listen(
        self,
        max_duration=8
    ):

        audio = self.record(
            max_duration=max_duration
        )

        if audio.size == 0:

            return {
                "text": "",
                "error": None
            }

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
                and os.path.exists(
                    temp_path
                )
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

    speech = SpeechToText(
        microphone_device=1
    )

    try:

        speech.calibrate()

        result = speech.listen(
            max_duration=8
        )

        print(
            "\nTRANSCRIPTION:"
        )

        print(
            result
        )

    finally:

        speech.close()