import torch
import requests
import json
import base64
import io
from PIL import Image
import numpy as np

class VideoPromptArchitect:
    """
    Video Prompt Architect: 支援雙圖轉場或單圖擴充的影片提示詞生成節點。
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start_image": ("IMAGE",),
                "user_description": ("STRING", {"multiline": True, "default": "A sunset to starry night"}),
                "system_role_instruction": ("STRING", {"multiline": True, "default": "You are a professional Cinematographer."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}),
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "end_image": ("IMAGE",),  # 將尾幀設為選填
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_en", "prompt_zh_tw", "prompt_zh_cn")
    FUNCTION = "execute_architect"
    CATEGORY = "VideoProduction/PromptEngine"

    def tensor_to_base64(self, image_tensor):
        """將 ComfyUI Tensor 轉換為 Base64 JPEG 字串"""
        img_np = (image_tensor[0].cpu().numpy() * 255).astype(np.uint8)
        img = Image.fromarray(img_np)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def execute_architect(self, start_image, user_description, system_role_instruction, 
                          api_url, model_name, api_key, max_new_tokens, temperature, end_image=None):
        
        # 1. 處理起始圖片 (必備)
        try:
            start_b64 = self.tensor_to_base64(start_image)
        except Exception as e:
            return (f"Start Image Error: {str(e)}", "", "")

        # 2. 判斷是否提供尾幀圖片並決定 Task 指令
        image_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{start_b64}"}}
        ]

        if end_image is not None:
            # 有提供尾幀：執行轉場分析
            try:
                end_b64 = self.tensor_to_base64(end_image)
                image_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{end_b64}"}})
                task_instruction = "Analyze the transition from the Start Image to the End Image. Describe the cinematic evolution, camera movement, and lighting changes between them."
            except Exception as e:
                return (f"End Image Error: {str(e)}", "", "")
        else:
            # 沒有提供尾幀：執行單圖擴充
            task_instruction = "Analyze the provided Start Image and expand it into a highly detailed cinematic scene description, focusing on atmosphere and visual depth."

        # 3. 構建最終 Master Prompt
        master_prompt = f"""
{system_role_instruction}

TASK:
{task_instruction}

USER'S CORE CONCEPT: "{user_description}"

OUTPUT FORMAT:
You must respond ONLY with a valid JSON object. Do not include any conversational text.
The JSON must follow this exact structure:
{{
    "en": "High-quality English prompt for video generation models",
    "tw": "繁體中文描述",
    "cn": "簡體中文描述"
}}
"""

        # 4. 準備 API Payload
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": master_prompt},
                        *image_content  # 將圖片內容解包放入列表
                    ]
                }
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "response_format": { "type": "json_object" } 
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 5. 發送 API 請求
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            res_data = response.json()
            
            content_str = res_data['choices'][0]['message']['content']
            content_json = json.loads(content_str)
            
            return (
                content_json.get("en", ""),
                content_json.get("tw", ""),
                content_json.get("cn", "")
            )

        except Exception as e:
            error_msg = f"API/Parsing Error: {str(e)}"
            print(error_msg)
            return (error_msg, error_msg, error_msg)