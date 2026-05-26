#!/usr/bin/env python3
"""
生成带有签名的纪念章JSON文件
使用方式:
from badge_generator import BadgeGenerator
generator = BadgeGenerator()
badge_data = generator.generate_badge({"姓名": "张三", "学号": "123456", "角色": "成员"})
"""

import json
import base64
import os
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class BadgeGenerator:
    def __init__(self, private_key_path="keys/private_key.pem"):
        """初始化签名器"""
        with open(private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    
    # 支持的媒体格式映射
    MEDIA_TYPES = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.ogg': 'video/ogg',
    }

    def encode_file_to_base64(self, file_path: str) -> str:
        """将文件编码为Base64字符串，包含data URL头"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = self.MEDIA_TYPES.get(ext, 'application/octet-stream')
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded}"
    
    def sign_data(self, json_str: str) -> str:
        """为JSON字符串生成Ed25519签名"""
        # 使用私钥签名（Ed25519会自动处理哈希）
        signature = self.private_key.sign(json_str.encode('utf-8'))
        
        # 将签名转为Base64字符串
        return base64.b64encode(signature).decode('utf-8')
    
    def generate_badge(self, data: dict) -> dict:
        """
        生成完整的纪念章数据
        
        Args:
            data: 任意dict，包含纪念章的所有属性
            
        Returns:
            扁平格式的纪念章数据，包含badge(JSON string)、signature、algorithm
            badge 格式: [{"key": "xxx", "value": "xxx"}, ...]
        """
        # 将 dict 转为数组格式，保持插入顺序
        badge_list = [{"key": k, "value": v} for k, v in data.items()]
        
        # 将数据转为规范化JSON字符串（确保空格一致）
        badge_str = json.dumps(badge_list, separators=(',', ':'), ensure_ascii=False)
        
        # 生成签名
        signature = self.sign_data(badge_str)
        
        # 返回扁平格式的数据
        return {
            "badge": badge_str,
            "signature": signature,
            "algorithm": "Ed25519"
        }
    
    def save_badge(self, badge_data: dict, filename: str = None):
        """保存纪念章到文件"""
        if not filename:
            # 尝试从badge数组中提取信息生成文件名
            try:
                badge_list = json.loads(badge_data["badge"])
                member_name = None
                student_id = None
                title = "badge"
                for item in badge_list:
                    if item["key"] in ("姓名", "member_name", "name"):
                        member_name = item["value"]
                    elif item["key"] in ("学号", "student_id", "member_student_id"):
                        student_id = item["value"]
                    elif item["key"] in ("标题", "badge_title"):
                        title = item["value"]
                if not member_name:
                    member_name = "unknown"
                if not student_id:
                    student_id = ""
                filename = f"badges/{student_id}_{member_name}_{title}.json"
            except:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"badges/badge_{timestamp}.json"
        
        os.makedirs("badges", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(badge_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 纪念章已生成: {filename}")
        return filename