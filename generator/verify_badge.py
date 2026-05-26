#!/usr/bin/env python3
"""
验证纪念章签名
使用方式:
from verify_badge import verify_badge
is_valid, badge_list = verify_badge("badge.json")
"""

import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def verify_badge(badge_file: str, public_key_path: str = "keys/public_key.pem"):
    """
    验证纪念章签名
    
    Args:
        badge_file: 纪念章JSON文件路径
        public_key_path: 公钥文件路径
        
    Returns:
        (is_valid, badge_list): (是否验证通过, 徽章信息数组 [{"key": "xxx", "value": "xxx"}, ...])
    """
    
    # 加载纪念章数据
    with open(badge_file, "r", encoding="utf-8") as f:
        badge_data = json.load(f)
    
    # 分离数据和签名（badge现在是JSON字符串）
    badge_str = badge_data["badge"]
    signature_b64 = badge_data["signature"]
    
    # 解析badge字符串为数组格式
    badge_list = json.loads(badge_str)
    
    # 加载公钥
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )
        
    # 解码签名
    signature_bytes = base64.b64decode(signature_b64)
    
    # 验证签名（Ed25519会自动处理哈希）
    # 直接使用badge字符串进行验证，不需要再次序列化
    try:
        public_key.verify(
            signature_bytes,
            badge_str.encode('utf-8')
        )
        return True, badge_list
    except InvalidSignature:
        return False, badge_list
    except Exception:
        return False, badge_list

def display_badge_info(badge_list: list):
    """美观地显示纪念章信息（遍历数组，保持顺序）"""
    print("\n" + "="*50)
    print("🏅 纪念章信息")
    print("="*50)
    for item in badge_list:
        key = item["key"]
        value = item["value"]
        # 将可能的英文key转换为中文显示
        key_display = {
            'member_name': '持有人',
            'member_student_id': '学号',
            'member_role': '角色',
            'club_name': '社团',
            'club_id': '社团ID',
            'badge_title': '标题',
            'badge_type': '类型',
            'badge_year': '年份',
            'badge_description': '描述',
            'issue_time': '颁发时间',
            'id': '唯一ID'
        }.get(key, key)
        # 处理空值或None
        value_display = value if value else '未设置'
        print(f"{key_display}: {value_display}")
    print("="*50)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python verify_badge.py <badge_file.json> [public_key.pem]")
        sys.exit(1)
    
    badge_file = sys.argv[1]
    public_key = sys.argv[2] if len(sys.argv) > 2 else "keys/public_key.pem"
    
    try:
        is_valid, badge_list = verify_badge(badge_file, public_key)
        
        if is_valid:
            print("✅ 验证通过！此纪念章真实有效。")
        else:
            print("❌ 验证失败！纪念章可能被篡改或签名无效。")
        display_badge_info(badge_list)
            
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
    except json.JSONDecodeError:
        print(f"❌ 文件格式错误: {badge_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")