#!/usr/bin/env python3
import os
import math
import shutil
import re
from dotenv import load_dotenv
from pydub import AudioSegment
from openai import OpenAI

# --------------------------------------------------
# .env 參數設定（請放在專案根目錄的 .env）：
#
# API_KEY               必填，OpenAI API 金鑰
# TRANSCRIBE_MODEL      選填，要使用的轉錄模型名稱，預設 gpt-4o-transcribe
# CHUNK_MINUTE          必填，切割音檔的長度（分鐘），建議 1～10
# AUDIO_FILE            必填，置於 input/ 資料夾中的音檔檔名
# PROMPT                選填，轉錄時提供給模型的提示文字，
#                       用 \n 表示換行；若留空則使用模型預設行為
# ENABLE_SEGMENTATION   選填，是否在句尾自動插入換行分段 (true/false)
# --------------------------------------------------


INPUT_DIR   = "input"
OUTPUT_DIR  = "output"
CHUNK_DIR   = "trans_chunks"


def load_env():
    """讀取 .env 參數並檢查必要欄位"""
    load_dotenv()
    api_key    = os.getenv("API_KEY")
    model_name = os.getenv("TRANSCRIBE_MODEL", "gpt-4o-transcribe")
    chunk_min  = os.getenv("CHUNK_MINUTE")
    audio_file = os.getenv("AUDIO_FILE")
    # 驗證必填
    if not api_key or not chunk_min or not audio_file:
        raise RuntimeError("請在 .env 裡設定 API_KEY、CHUNK_MINUTE、AUDIO_FILE")
    try:
        chunk_min = int(chunk_min)
    except ValueError:
        raise RuntimeError("CHUNK_MINUTE 必須是整數")
    prompt     = os.getenv("PROMPT") or None
    enable_seg = os.getenv("ENABLE_SEGMENTATION", "false").lower() in ("1","true","yes")
    return api_key, model_name, chunk_min, audio_file, prompt, enable_seg


def split_audio(in_path, chunk_min):
    """將輸入音檔依分鐘長度切片，並儲存在 CHUNK_DIR 中。"""
    audio        = AudioSegment.from_file(in_path)
    duration_ms  = len(audio)
    ms_per_chunk = chunk_min * 60 * 1000
    os.makedirs(CHUNK_DIR, exist_ok=True)
    base         = os.path.splitext(os.path.basename(in_path))[0]

    paths = []
    num_chunks = math.ceil(duration_ms / ms_per_chunk)
    for i in range(num_chunks):
        start   = i * ms_per_chunk
        end     = min((i+1) * ms_per_chunk, duration_ms)
        segment = audio[start:end]
        fn      = f"{base}_chunk_{i+1:03d}.mp3"
        dst     = os.path.join(CHUNK_DIR, fn)
        segment.export(dst, format="mp3")
        paths.append(dst)
        print(f"Exported {dst} ({start//1000}s–{end//1000}s)")
    return paths


def transcribe_chunks(chunks, client, model_name, prompt):
    """依序呼叫 OpenAI API 轉錄每段音檔，回傳合併後的文字結果。"""
    transcripts = []
    for idx, path in enumerate(chunks, 1):
        print(f"[{idx}/{len(chunks)}] Transcribing {path} …")
        with open(path, "rb") as af:
            params = {
                "model": model_name,
                "file": af,
                "response_format": "text",
            }
            # 若使用者自訂 prompt，就鎖定 temperature=0.0；否則使用模型預設隨機性
            if prompt:
                params["prompt"]     = prompt
                params["temperature"] = 0.0
            resp = client.audio.transcriptions.create(**params)
        transcripts.append(resp)
        print(f"  → Done segment {idx}")
    return "\n\n".join(transcripts)


def main():
    api_key, model_name, chunk_min, audio_file, prompt, enable_seg = load_env()
    client = OpenAI(api_key=api_key)

    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_path = os.path.join(INPUT_DIR, audio_file)
    if not os.path.isfile(input_path):
        raise RuntimeError(f"在 {INPUT_DIR} 找不到檔案：{audio_file}")

    # 1) 切割音檔
    chunks = split_audio(input_path, chunk_min)

    # 2) 轉錄並取得完整文字
    full_text = transcribe_chunks(chunks, client, model_name, prompt)

    # 3) 如啟用句尾分段，自動在常見句尾標點後插入換行
    if enable_seg:
        full_text = re.sub(r'([。！？\?\.])', r'\1\n', full_text)

    # 4) 寫入輸出檔案
    base        = os.path.splitext(os.path.basename(input_path))[0]
    result_path = os.path.join(OUTPUT_DIR, f"{base}.txt")
    with open(result_path, "w", encoding="utf-8") as fout:
        fout.write(full_text)
    print(f"→ Saved transcript to {result_path}")

    # 5) 清理暫存切片資料夾
    if os.path.isdir(CHUNK_DIR):
        shutil.rmtree(CHUNK_DIR)
        print(f"→ Removed {CHUNK_DIR}")

if __name__ == "__main__":
    main()