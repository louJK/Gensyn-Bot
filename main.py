import os
import json
import requests
import time
from datetime import datetime
from node_tasks import NodeTaskManager

CONFIG_FILE = "config.json"

# Khởi tạo bộ quản lý thống kê node
task_manager = NodeTaskManager()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ Không tìm thấy file cấu hình. Vui lòng chạy: python setup.py")
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def send_telegram_message(token, chat_id, message: str):
    """Gửi tin nhắn Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    return requests.post(url, json=payload)

def fetch_peer_data(peer_info):
    """Lấy thông tin node — hỗ trợ cấu hình theo ID hoặc theo tên cũ"""
    if isinstance(peer_info, dict):
        # Định dạng mới: { "id": "...", "remark": "Server A" }
        peer_id = peer_info.get("id")
        remark = peer_info.get("remark", "")
    else:
        # Tương thích định dạng cũ: chỉ có tên node
        peer_id = None
        remark = ""

    # Ưu tiên truy vấn bằng ID
    if peer_id:
        url = f"https://dashboard.gensyn.ai/api/v1/peer?id={peer_id}"
    else:
        # Tương thích bản cũ (query theo tên)
        url_name = peer_info.replace(" ", "%20")
        url = f"https://dashboard.gensyn.ai/api/v1/peer?name={url_name}"
    
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()

            # Nếu query bằng tên, cập nhật peer_id
            if not peer_id and "peerId" in data:
                peer_id = data["peerId"]

            task_manager.update_node_stats(
                peer_id,
                data.get("reward", 0),
                data.get("score", 0),
                data.get("online", False)
            )

            # Thêm ghi chú hiển thị
            data["_remark"] = remark
            return data

    except Exception as e:
        print(f"❌ Lỗi lấy dữ liệu node: {str(e)}")
    
    return None

def format_node_status(info, peerno, previous_data=None):
    """Tạo định dạng thông báo node"""
    peer_id = info["peerId"]
    reward = info.get("reward", 0)
    score = info.get("score", 0)
    online = info.get("online", False)
    remark = info.get("_remark", "")

    stats_changes = task_manager.get_stats_change(peer_id)
    changes = []

    # So sánh với dữ liệu trước đó
    if previous_data:
        prev_reward = previous_data.get("reward", 0)
        prev_score = previous_data.get("score", 0)
        prev_online = previous_data.get("online", False)

        if reward != prev_reward:
            change = reward - prev_reward
            changes.append(f"R:{prev_reward}→{reward}({change:+.0f})")

        if score != prev_score:
            change = score - prev_score
            changes.append(f"S:{prev_score}→{score}({change:+.0f})")

        if online != prev_online:
            changes.append("🟢 Online" if online else "🔴 Offline")

    status_icon = "🟢" if online else "🔴"
    change_text = " | " + " | ".join(changes) if changes else ""

    # Hiển thị tên: ưu tiên remark, nếu không có thì hiển thị ID rút gọn
    display_name = remark if remark else f"Node_{peer_id[:12]}"

    msg = f"<b>{peerno}</b> {status_icon} <code>{display_name}</code>\n"
    msg += f"R:{reward} | S:{score} | ID:{peer_id[:12]}...{change_text}"

    # Thêm phần thống kê xu hướng
    if stats_changes:
        msg += "\n📊 Xu hướng: "
        trend_parts = []
        if 'reward' in stats_changes:
            trend_parts.append(f"R:{stats_changes['reward']['change']:+.0f}")
        if 'score' in stats_changes:
            trend_parts.append(f"S:{stats_changes['score']['change']:+.0f}")
        if 'online' in stats_changes:
            trend_parts.append("🟢 Online" if stats_changes['online']['current'] else "🔴 Offline")
        msg += " | ".join(trend_parts)

    return msg

def query_nodes_status(config, chat_id):
    """Kiểm tra trạng thái tất cả node"""
    try:
        messages = []
        current_data = {}

        for peer_info in config["PEER_NAMES"]:
            data = fetch_peer_data(peer_info)
            if data:
                current_data[data["peerId"]] = data

        for i, (peer_id, info) in enumerate(current_data.items(), 1):
            messages.append(format_node_status(info, i))

        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"<b>📊 Trạng thái Node Gensyn ({timestamp})</b>\n\n"
        full_message += "\n".join(messages)

        response = send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, full_message)

        if not response.ok:
            send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, "❌ Lỗi truy vấn. Vui lòng thử lại.")

    except Exception as e:
        send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, f"❌ Lỗi truy vấn: {str(e)}")

def get_updates(config, offset=None):
    """Nhận cập nhật từ Telegram"""
    url = f"https://api.telegram.org/bot{config['TELEGRAM_API_TOKEN']}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"❌ Lỗi lấy cập nhật Telegram: {str(e)}")

    return None

def process_message(config, message):
    """Xử lý tin nhắn từ Telegram"""
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    # Chỉ cho phép Chat ID đã cấu hình
    if str(chat_id) != config["CHAT_ID"]:
        return

    if text == '/start':
        welcome_msg = """🤖 <b>Bot Giám Sát Node Gensyn</b>

Các lệnh khả dụng:
/status - Xem trạng thái toàn bộ node
/help - Hướng dẫn sử dụng

Bot sẽ hiển thị Reward, Score và trạng thái Online/Offline của node.
"""
        send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, welcome_msg)

    elif text == '/status':
        send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, "⏳ Đang lấy dữ liệu node...")
        query_nodes_status(config, chat_id)

    elif text == '/help':
        help_msg = """📘 <b>Hướng dẫn</b>

<b>Các lệnh:</b>
• /start - Khởi động bot
• /status - Kiểm tra tất cả node
• /help - Xem hướng dẫn

<b>Ý nghĩa trạng thái:</b>
🟢 Online
🔴 Offline
R: Reward
S: Score
ID: Peer ID (12 ký tự đầu)

<b>Phát hiện thay đổi:</b>
Bot sẽ tự động hiển thị thay đổi Reward, Score và trạng thái Online/Offline.
"""
        send_telegram_message(config["TELEGRAM_API_TOKEN"], chat_id, help_msg)

def main():
    config = load_config()
    if not config:
        return

    print("🤖 Bot Giám Sát Node Gensyn – Chế độ Telegram")
    print("Bot đã khởi động. Gửi lệnh từ Telegram:")
    print("- /start - Khởi động bot")
    print("- /status - Xem trạng thái node")
    print("- /help - Hướng dẫn")

    offset = None

    while True:
        try:
            updates = get_updates(config, offset)
            if updates and updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    if 'message' in update:
                        process_message(config, update['message'])
                    offset = update['update_id'] + 1

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Đã dừng bot.")
            break
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            time.sleep(5)  # Tránh spam khi lỗi

if __name__ == "__main__":
    main()
