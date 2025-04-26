from pathlib import Path
import datetime as dt
import os

class Saver:
    """把逐句結果寫進檔案，也保留在 memory 給後續摘要用。"""
    def __init__(self, folder: str = "transcripts"):
        try:
            Path(folder).mkdir(exist_ok=True)
        except Exception as e:
            print(f"創建目錄 {folder} 失敗: {e}")
            raise
        # 使用時間戳來避免檔案名稱衝突
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = Path(folder) / f"transcript_{timestamp}.txt"
        self.memory = []
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.file_counter = 0

    def __call__(self, text: str, ts):
        line = f"{ts:%H:%M:%S}  {text}\n"
        self.memory.append(text)
        try:
            # 檢查檔案大小，超過限制則創建新檔案
            if self.path.exists() and os.path.getsize(self.path) >= self.max_file_size:
                self.file_counter += 1
                timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.path = self.path.parent / f"transcript_{timestamp}_{self.file_counter}.txt"
                print(f"檔案大小超出限制，創建新檔案: {self.path}")
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            print(f"寫入檔案 {self.path} 失敗: {e}")
