# Video Prompt Architect (多模態影片提示詞架構師)
[![Author](https://img.shields.io/badge/Author-Jetter-blue.svg)](https://github.com/JetterTW)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  

**Video Prompt Architect** 是一個專為影片生成工作流設計的高級 ComfyUI 節點。它透過多模態大型語言模型 (Multimodal LLM) 同時分析「起始圖片」與「結束圖片」，並結合使用者的角色指令，自動生成描述影像轉場、運鏡、光影變化與風格演進的高品質影片提示詞。

本專案支援同時輸出 **英文 Prompt** (用於影片生成模型) 與 **繁體/簡體中文 Prompt** (用於內容理解)，讓你在設計動態轉場時能精準掌控 AI 的生成細節。

## ✨ 功能特點
* **🖼️ 多模態視覺分析**: 獨特的雙圖(或單圖)輸入機制，讓 LLM 能理解從第一張圖到第二張圖之間的動態演變趨勢。
* **🎬 전문電影級描述**: 自動針對運鏡方式 (Camera Movement)、光影轉換 (Lighting Transitions) 與環境氛圍進行細節擴充。
* **🎭 角色導向生成**: 透過 `system_role_instruction` 隨意定義 LLM 的專業身分（如：電影導演、MV 導演、特效專家）。
* **🌓 三語輸出機制**: 同時生成英文、繁體中文、簡體中文，兼顧繪圖實用性與視覺理解。
* **🔌 全兼容 API 介面**: 採用 OpenAI API 標準格式，支援幾乎所有主流多模態 LLM 後端（如 LM Studio, Ollama, vLLM 等）。
* **🛡️ 穩定 JSON 解析**: 內建強大的 JSON 解析機制，確保輸出結果能精準拆分至三個不同的輸出埠，不會因模型多餘字元而導致工作流中斷。

## 🚀 安裝方法
1. 進入您的 `ComfyUI/custom_nodes` 目錄。
2. 使用 Git 下載本專案：
   ```bash
   git clone https://github.com/JetterTW/ComfyUI-Video-Prompt-Architect.git
   
3. 進入資料夾並確保已安裝依賴套件：
   ```bash
   pip install -r requirements.txt

4. 重啟 ComfyUI。

## 🛠 參數說明
| 參數 | 類型 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `start_image` | IMAGE | - | 影片起始幀的圖片。 |
| `end_image` | IMAGE | - | 影片結束幀的圖片(可省略)。 |
| `user_description` | STRING | `A sunset to starry night` | 您輸入的原始轉場構想。 |
| `system_role_instruction` | STRING | `You are a professional...` | 設定 LLM 的角色與任務指令。 |
| `api_url` | STRING | `http://127.0.0.1:1234/v1/chat/completions` | LLM API 的端點網址。 |
| `model_name` | STRING | `gemma4` | 指定要使用的多模態模型名稱。 |
| `api_key` | STRING | `not-needed` | API 認證金鑰 (本地模型通常填 `not-needed`)。 |
| `max_new_tokens` | INT | `2048` | 生成文字的最大長度上限。 |
| `temperature` | FLOAT | `0.7` | 創意程度 (0.0 - 2.0)。越高越具想像力。 |

## 💡 使用範例
### 場景一: 使用本地 LM Studio 進行影片轉場設計
* **api_url**: `http://127.0.0.1:1234/v1/chat/completions`
* **model_name**: `local-vision-model`
* **system_role_instruction**: `You are a professional Cinematographer.`

### 場景二: 連接遠端多模態伺服器
* **api_url**: `http://192.168.1.9:8000/v1/chat/completions`
* **model_name**: `gemma4`

## 📋 推薦工作流 (Workflow)
1. **Input**: 使用 `Video Prompt Architect` 輸入起始圖、結束圖與轉場想法。
2. **Generation**: 將 **prompt_en** 輸出端連接至影片生成節點 (如 Runway/Luma API 或相關 ComfyUI 影片節點)。
3. **Review**: 將 **prompt_zh_tw** 輸出端連接至 `Show Text` 節點，確認轉場描述（如運鏡、光影）是否符合預期。

## 系統提示詞
在 [SystemPrompt.md](SystemPrompt.md) 中有提供幾個常用的系統提示詞。

## ⚠️ 注意事項
* **模型支援**: 務必使用支援 **Vision (多模態)** 功能的模型（例如 Gemma 4, Llama-3-Vision 等），否則節點無法讀取圖片內容。
* **URL 格式**: 請確保 API URL 指向的是 `/chat/completions` 結尾的完整路徑。
* **網路環境**: 若連接遠端 IP, 請確保網路連線暢通且該伺服器的 Port 已開啟。

## 🤝 貢獻與回報
如果您發現任何問題或有改進建議, 歡迎提交 Issue 或 Pull Request。

---
**Author:** [Jetter](https://github.com/JetterTW)
**License:** MIT
