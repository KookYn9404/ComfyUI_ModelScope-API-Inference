import os
import sys
import base64
import requests
from io import BytesIO
from PIL import Image

class KOOK_ModelScope_Vision:
    """KOOK魔搭反推节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点的输入类型"""
        return {
            "required": {
                "image": ("IMAGE",),
                "base_url": ("STRING", {"default": "https://api-inference.modelscope.cn/v1", "multiline": False}),
                "api_key": ("STRING", {"default": "", "multiline": False, "placeholder": "ModelScope Token"}),
                "text": ("STRING", {"default": "描述这幅图", "multiline": True, "placeholder": "输入你的自定义要求"}),
                "model": ("STRING", {"default": "Qwen/Qwen3-VL-8B-Instruct", "multiline": False}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_output",)
    FUNCTION = "run_inference"
    CATEGORY = "KOOK魔搭反推"
    
    def run_inference(self, image, base_url, api_key, text, model):
        """执行推理"""
        # 处理图片
        i = 255. * image[0].cpu().numpy()
        img = Image.fromarray(i.astype('uint8'))
        
        # 将图片转换为base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_url = f"data:image/png;base64,{img_str}"
        
        # 构建请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }],
            "stream": False
        }
        
        # 发送请求
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return (content,)
            else:
                return ("Error: No choices in response",)
        else:
            return (f"Error: {response.status_code} - {response.text}",)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "KOOK_ModelScope_Vision": KOOK_ModelScope_Vision
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KOOK_ModelScope_Vision": "魔搭API调用反推节点"
}