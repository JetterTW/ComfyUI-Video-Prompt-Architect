import torch
import requests
import json
import base64
import io
import numpy as np
from PIL import Image

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
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "end_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_en", "prompt_zh_tw", "prompt_zh_cn")
    FUNCTION = "execute_architect"
    CATEGORY = "VideoProduction/PromptEngine"

    def tensor_to_base64(self, image_tensor):
        img_np = (image_tensor[0].cpu().numpy() * 255).astype(np.uint8)
        img = Image.fromarray(img_np)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def execute_architect(self, start_image, user_description, system_role_instruction,
                          api_url, model_name, api_key, max_new_tokens, temperature, seed, end_image=None):
        
        try:
            start_b64 = self.tensor_to_base64(start_image)
        except Exception as e:
            return (f"Start Image Error: {str(e)}", "", "")

        image_content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{start_b64}"}}]
        
        if end_image is not None:
            try:
                end_b64 = self.tensor_to_base64(end_image)
                image_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{end_b64}"}})
                task_instruction = "Analyze the transition from the Start Image to the End Image. Describe the cinematic evolution, camera movement, and lighting changes between them."
            except Exception as e:
                return (f"End Image Error: {str(e)}", "", "")
        else:
            task_instruction = "Analyze the provided Start Image and expand it into a highly detailed cinematic scene description, focusing on atmosphere and visual depth."

        # 用 seed 擾動 prompt，確保每次輸入都不一樣
        noise = f" [ID:{seed}]"

        master_prompt = f"""
{system_role_instruction}

TASK:
{task_instruction}

USER'S CORE CONCEPT: "{user_description}"

IMPORTANT RULE:
Respond ONLY with a raw JSON object. 
DO NOT include any reasoning, internal monologue, or any text before or after the JSON. 
No tags, no explanation, just the JSON.

OUTPUT FORMAT:
{{
    "en": "English prompt",
    "tw": "繁體中文",
    "cn": "简体中文"
}}
{noise}
"""

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": master_prompt},
                        *image_content
                    ]
                }
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "response_format": { "type": "json_object" },
            "seed": seed
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            res_data = response.json()
            content_str = res_data['choices'][0]['message']['content']

            # 這裡我們用最簡單的字串方法，只抓取 { 到 } 之間的內容
            # 這能有效避開任何可能出現在 JSON 外面的廢話
            start_idx = content_str.find('{')
            end_idx = content_str.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = content_str[start_idx:end_idx+1]
                content_json = json.loads(json_str)
                return (
                    content_json.get("en", ""),
                    content_json.get("tw", ""),
                    content_json.get("cn", "")
                )
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return (error_msg, error_msg, error_msg)

NODE_CLASS_MAPPINGS = {"VideoPromptArchitect": VideoPromptArchitect}
NODE_DISPLAY_NAME_MAPPINGS = {"VideoPromptArchitect": "Video Prompt Architect"}
