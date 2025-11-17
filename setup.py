#!/usr/bin/env python3
"""
Trình cài đặt nhanh - Bot giám sát Gensyn Node
"""

import os
import sys
import json
import subprocess

def print_banner():
    """In banner mở đầu"""
    print("🤖" + "="*50 + "🤖")
    print("    Bot Giám Sát Gensyn Node - Cài Đặt Nhanh")
    print("🤖" + "="*50 + "🤖")

def print_telegram_guide():
    """Hướng dẫn tạo Telegram Bot"""
    print("\n📱 Vui lòng tạo Telegram Bot theo hướng dẫn trong README.md")
    print("   Sau khi có Bot Token và Chat ID hãy quay lại bước này.")

def get_telegram_config():
    """Lấy cấu hình Telegram từ người dùng"""
    print("\n🔧 Cấu hình Telegram Bot")
    print("-" * 30)
    
    config = {}
    config["TELEGRAM_API_TOKEN"] = input("Nhập Bot Token: ").strip()
    config["CHAT_ID"] = input("Nhập Chat ID của bạn: ").strip()
    return config

def get_monitoring_config():
    """Lấy danh sách node cần theo dõi"""
    print("\n📊 Cấu hình danh sách Node giám sát")
    print("-" * 30)
    
    print("Nhập thông tin node (hỗ trợ 2 dạng):")
    print("Dạng 1 - Tên node đơn giản: loud sleek bat")
    print("Dạng 2 - ID + ghi chú: id,ghi_chu")
    print("Ví dụ: Qmb14s2Es99SDQ...,Server A")
    print("⚠️ Dùng dấu phẩy để phân tách nhiều mục.")
    
    nodes_input = input("Nhập danh sách node: ").strip()
    nodes = [node.strip() for node in nodes_input.split(",") if node.strip()]
    
    config = {}
    peer_names = []
    
    for i in range(0, len(nodes), 2):
        if i + 1 < len(nodes):
            # Có dạng id + remark
            peer_id = nodes[i]
            remark = nodes[i + 1]
            peer_names.append({
                "id": peer_id,
                "remark": remark
            })
        else:
            # Chỉ có tên node (dạng cũ)
            peer_names.append(nodes[i])
    
    config["PEER_NAMES"] = peer_names
    return config

def save_config(config):
    """Lưu cấu hình vào file"""
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Đã lưu cấu hình vào config.json")

def main():
    print_banner()
    
    # Kiểm tra Python
    if sys.version_info < (3, 7):
        print("❌ Cần Python 3.7 trở lên")
        sys.exit(1)
    
    # Kiểm tra dependency
    try:
        import requests
    except ImportError:
        print("📦 Đang cài đặt gói phụ thuộc...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print_telegram_guide()
    
    # Lấy cấu hình
    telegram_config = get_telegram_config()
    monitoring_config = get_monitoring_config()
    
    # Gộp lại
    config = {**telegram_config, **monitoring_config}
    
    # Lưu file
    save_config(config)
    
    print("\n🎉 Cài đặt hoàn tất!")
    print("\nTiếp theo:")
    print("➡️  Chạy: python main.py")
    print("➡️  Sau đó nhập lệnh /status trong Telegram để xem node")

if __name__ == "__main__":
    main()
