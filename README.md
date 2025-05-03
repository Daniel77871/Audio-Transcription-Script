# Audio Transcription Script

**將大型音檔切割、上傳至 OpenAI 轉錄，並合併成文字檔。**

---

## 目錄
1. [介紹](#介紹)  
2. [前置需求](#前置需求)  
3. [安裝步驟](#安裝步驟)  
4. [配置 `.env`](#配置-env)  
5. [使用方式](#使用方式)  
6. [資料夾結構](#資料夾結構)  
7. [注意事項](#注意事項)  

---

## 介紹
本專案提供一支 Python 腳本 (`Transcriptions.py`)，可將大型音檔（如 `.m4a`、`.mp3`）自動切割成多段，依序呼叫 OpenAI 的轉錄模型進行聽寫，最後合併為單一文字檔。

- 可自訂 **轉錄模型**（如 `gpt-4o-transcribe`、`whisper-1` 等）。  
- 支援 **使用者提示**（Prompt）以提升準確度。  
- 可選擇在 **句尾自動換行分段**，或一次輸出連續段落。  

---

## 前置需求

-   **Python 3.8+（已知問題：Python 3.13+不支援）**
-   **OpenAI API Key**
    -   請至 OpenAI 帳號設定 申請並取得 API Key
-   **ffmpeg**
    -   **Windows**（以 Chocolatey 套件管理為例）
        -   開啟「以管理員身分執行」的命令提示字元（CMD）
        -   執行：
            ```bash
            choco install ffmpeg
            ```
    -   **macOS / Linux**
        ```bash
        brew install ffmpeg         # macOS（需先安裝 Homebrew）
        sudo apt update && sudo apt install ffmpeg  # Ubuntu / Debian
        ```
-   **Python 套件**
    -   `python-dotenv`：讀取 `.env`
    -   `pydub`：音檔讀取與切割
    -   `openai`：連接 OpenAI API
    -   建議使用虛擬環境（venv、conda 或其他）

---

## 安裝步驟

1.  **Clone 本專案**
    ```bash
    git clone https://github.com/Daniel77871/Audio-Transcription-Script.git
    cd Audio-Transcription-Script
    ```
2.  **建立並啟用虛擬環境**
    ```bash
    python3 -m venv venv
    # macOS / Linux
    source venv/bin/activate
    # Windows (PowerShell)
    .\venv\Scripts\Activate.ps1
    ```
3.  **安裝 Python 依賴**
    ```bash
    pip install --upgrade pip
    pip install python-dotenv pydub openai
    ```

---

## 配置 `.env`

在專案根目錄下建立 `.env`，填入以下參數：

```dotenv
# —————— 必填 ——————
# 你的 OpenAI API Key
API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 要使用的轉錄模型名稱，預設 gpt-4o-transcribe
TRANSCRIBE_MODEL=gpt-4o-transcribe

# 將音檔切割成每段幾分鐘（建議 1～10 分鐘）
CHUNK_MINUTE=10

# 欲處理的音檔檔名（請放在 input/ 資料夾內）
AUDIO_FILE=your_audio_filename.m4a

# —————— 選填 ——————
# 轉錄提示文字，若不需要可刪除或留空
PROMPT="請將以下語音內容完整轉錄，務必符合以下要求：\n1. 全部輸出請使用繁體中文，絕對不要使用簡體中文。\n2. 保留原文中所有英文單字、片語或專有名詞，不要翻譯或替換。\n3. 確保轉錄內容完整且正確，務必包含所有標點符號。\n4. 請勿分段，所有文字以連貫自然的完整段落呈現。\n5. 對於聽不清或無法辨識的部分，請以「[不確定]」標示。"

# 是否在句尾自動插入換行分段 (true/false)
ENABLE_SEGMENTATION=true
```
- `PROMPT` 如不需要，可刪除或留空。

- `ENABLE_SEGMENTATION` 設為 `true` 時，每句自動斷行；設為 `false` 則輸出一段。

確保 `input/` 資料夾已有欲轉錄的音檔。

---

## 使用方式

1.  **把音檔放進 `input/`**

    ```text
    input/
        your_audio_filename.m4a
    ```
2.  **執行轉錄腳本**
    ```bash
    python Transcriptions.py
    ```
3.  **轉錄結果**
    完成後，`output/` 會產生同名 `.txt`：
    ```text
    output/
        your_audio_filename.txt
    ```
    中間暫存的 `trans_chunks/` 資料夾會被強制刪除，不留任何切片檔。

---

## 專案資料夾結構

```text
transcription-script/
├── .env
├── Transcriptions.py
├── input/             # 放置原始音檔
│   └── (例如 your_audio_filename.m4a)
├── output/            # 轉錄後文字檔輸出位置
│   └── (例如 your_audio_filename.txt)
├── trans_chunks/      # 暫存切檔用，中間執行時建立，最後自動刪除
└── README.md
```

---

## 注意事項

-   **ffmpeg**：pydub 依賴 ffmpeg 進行編碼/解碼，請先完成安裝並確保 ffmpeg -version 可正常顯示。
-   **大檔案**：若音檔過大，建議增大 CHUNK_MINUTE 或分批處理，以免觸發網路或 API 超時。
-   **API 配額**：轉錄過程會呼叫 OpenAI API，請注意帳號配額與費用。
