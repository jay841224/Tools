import argparse
import datetime as dt
import sys
from rich.console import Console
from rich.text import Text

from transcribe import Transcriber
from storage import Saver

def main():
    parser = argparse.ArgumentParser(
        description="離線即時語音轉文字（faster-whisper medium）")
    parser.add_argument("--model", default="medium", help="Whisper 模型大小")
    parser.add_argument("--device", default="auto", help="設備類型 (auto, cpu, cuda)")
    parser.add_argument("--lang", default="zh", help="語言代碼")
    parser.add_argument("--compute-type", default="int8", help="計算類型 (int8, float16 等)")
    parser.add_argument("--sample-rate", type=int, default=16000, help="音頻採樣率")
    parser.add_argument("--chunk-ms", type=int, default=30, help="音頻塊大小（毫秒）")
    parser.add_argument("--vad-mode", type=int, default=2, choices=range(0, 4), help="VAD 模式，0-3，越大越敏感")
    parser.add_argument("--no-console", action="store_true", help="禁用控制台輸出")
    args = parser.parse_args()

    console = Console() if not args.no_console else None
    saver = Saver()
    try:
        transcriber = Transcriber(
            model_size=args.model,
            device=args.device,
            compute_type=args.compute_type,
            lang=args.lang,
            sample_rate=args.sample_rate,
            chunk_ms=args.chunk_ms,
            vad_mode=args.vad_mode
        )
    except Exception as e:
        print(f"初始化轉錄器失敗: {e}")
        sys.exit(1)

    def on_text(text, ts):
        saver(text, ts)  # 寫檔 & 暫存
        if console:
            console.print(Text.from_markup(
                f"[bold green]{ts:%H:%M:%S}[/] {text}"
            ))

    if console:
        console.rule(f"[cyan]開始錄音 {dt.datetime.now():%Y-%m-%d %H:%M:%S}")
    try:
        transcriber.listen(on_text)
    except KeyboardInterrupt:
        print("\n錄音已停止")
        sys.exit(0)
    except Exception as e:
        print(f"錄音過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
