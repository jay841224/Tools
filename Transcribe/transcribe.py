import queue, time, datetime as dt
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel

class Transcriber:
    def __init__(
        self,
        model_size: str = "medium",
        device: str = "auto",          # Apple GPU；Linux+NVIDIA 換成 cuda
        compute_type: str = "int8",
        lang: str = "zh",
        sample_rate: int = 16_000,
        chunk_ms: int = 30,
        vad_mode: int = 2             # 0~3：越大越敏感
    ):
        self.sample_rate = sample_rate
        self.chunk_bytes = sample_rate * chunk_ms // 1000 * 2   # int16 → 2 bytes
        self.q = queue.Queue()
        self.vad = webrtcvad.Vad(vad_mode)
        self.model = WhisperModel(model_size, device=device,
                                  compute_type=compute_type)
        self.lang = lang

    # ── Public API ─────────────────────────────────────────────
    def listen(self, on_text):
        """持續監聽麥克風並於偵測到一句話結束時觸發 on_text(str, ts)"""
        # 時間觸發閾值：每隔幾秒強制轉錄
        time_threshold = 2  # 秒
        last_trigger = time.time()
        max_buffer_size = self.sample_rate * 30  # 限制緩衝區大小為30秒的音頻數據

        buf, speaking = b'', False

        def audio_callback(indata, frames, t, status):
            if status:
                print(f"音頻回調狀態異常: {status}")
            self.q.put(bytes(indata))

        try:
            with sd.RawInputStream(self.sample_rate,
                                   blocksize=self.chunk_bytes // 2,
                                   dtype='int16', channels=1,
                                   callback=audio_callback):
                while True:
                    try:
                        buf += self.q.get()
                        # 限制緩衝區大小
                        if len(buf) > max_buffer_size:
                            buf = buf[-max_buffer_size:]
                            
                        if len(buf) < self.sample_rate:  # <1 秒
                            if time.time() - last_trigger >= time_threshold:
                                if buf:
                                    ts = dt.datetime.now()
                                    text = self._transcribe(buf)
                                    if text:
                                        on_text(text, ts)
                                    buf = b''
                                last_trigger = time.time()
                            continue

                        # VAD 決定此段是否含語音
                        voiced = any(
                            self.vad.is_speech(buf[i:i + self.chunk_bytes],
                                               self.sample_rate)
                            for i in range(0, len(buf), self.chunk_bytes)
                        )
                        if voiced:
                            speaking = True
                            if time.time() - last_trigger >= time_threshold:
                                if buf:
                                    ts = dt.datetime.now()
                                    text = self._transcribe(buf)
                                    if text:
                                        on_text(text, ts)
                                    buf = b''
                                last_trigger = time.time()
                            continue

                        if speaking:  # 剛結束一句
                            ts = dt.datetime.now()
                            text = self._transcribe(buf)
                            if text:
                                on_text(text, ts)
                            buf, speaking = b'', False
                        else:
                            buf = b''
                    except Exception as e:
                        print(f"處理音頻數據時發生錯誤: {e}")
                        buf = b''  # 重置緩衝區以避免進一步問題
        except Exception as e:
            print(f"音頻流初始化或運行時發生錯誤: {e}")

    # ── Internal helpers ──────────────────────────────────────
    def _transcribe(self, pcm_bytes: bytes) -> str:
        try:
            import io
            import wave
            # 將 PCM 數據轉換為 WAV 格式
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 單聲道
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(pcm_bytes)
            wav_io.seek(0)
            # 使用更快的設置以提高轉錄速度
            segments, _ = self.model.transcribe(
                wav_io, language=self.lang, beam_size=1, best_of=1, patience=1.0)
            return ''.join(seg.text for seg in segments)
        except Exception as e:
            print(f"轉錄過程中發生錯誤: {e}")
            return ""
