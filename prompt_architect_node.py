import torch
import requests
import json
import base64
import io
from PIL import Image
import numpy as np

class VideoPromptArchitect:
    """
    透過多模態 LLM 分析起始與結束圖片，並根據使用者角色與描述，
    生成用於影片生成工具（如 Runway, Luma, Kling）的高品質轉場 Prompt。
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start_image": ("IMAGE",),
                "end_image": ("IMAGE",),
                "user_description": ("STRING", {"multiline": True, "default": "A beautiful sunset transforming into a starry night"}),
                "system_role_instruction": ("STRING", {"multiline": True, "default": "You are a professional Cinematographer and Visual Effects Director."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}),
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    # 3個輸出: 英文, 繁中, 簡中
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_en", "prompt_zh_tw", "prompt_zh_cn")
    FUNCTION = "execute_architect"
    CATEGORY = "VideoProduction/PromptEngine"

    def tensor_to_base64(self, image_tensor):
        """將 ComfyUI Tensor 轉換為 Base64 JPEG 字串"""
        # ComfyUI Tensor: [Batch, Height, Width, Channels], Range 0.0-1.0
        img_np = (image_tensor[0].cpu().numpy() * 255).astype(np.uint8)
        img = Image.fromarray(img_np)
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def execute_architect(self, start_image, end_image, user_description, system_role_instruction, 
                          api_url, model_name, api_key, max_new_tokens, temperature):
        
        # 1. 影像轉碼
        try:
            start_b64 = self.tensor_to_base64(start_image)
            end_b64 = self.tensor_to_base64(end_image)
        except Exception as e:
            return (f"Image conversion error: {str(e)}", "", "")

        # 2. 構建指令
        # 強制要求 JSON 輸出以利自動拆分輸出埠
        master_prompt = f"""
{system_role_instruction}

TASK:
Analyze the 'Start Image' and 'End Image' provided. 
Your goal is to describe a seamless cinematic video transition from the first image to the second.
The description should focus on:
1. Motion: Camera movement (e.g., dolly in, crane shot, pan, tilt, zoom).
2. Lighting & Atmosphere: Changes in light, shadows, weather, or color grading.
3. Temporal Evolution: How the elements within the scene evolve over time.
4. Style: Maintain the visual style of the images.

USER'S CORE CONCEPT: "{user_description}"

OUTPUT FORMAT:
You must respond ONLY with a valid JSON object. Do not write any introduction or conclusion.
The JSON must follow this exact structure:
{{
    "en": "High-quality English prompt for video generation models",
    "tw": "繁體中文描述",
    "cn": "简体中文描述"
}}
"""

        # 3. 準備 API Payload
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": master_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{start_b64}"}
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{end_b64}"}
                        }
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

        # 4. 發送 API 請求
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
            