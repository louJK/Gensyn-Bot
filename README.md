# 🤖 Gensyn Node Monitor Bot

Đây là một Telegram Bot giúp bạn theo dõi trạng thái các **Gensyn Node**, bao gồm Reward, Score, tình trạng Online và các thay đổi theo thời gian.

---

## ✨ Tính năng nổi bật
- 🔍 Tra cứu trạng thái node qua lệnh Telegram  
- 📊 Theo dõi thay đổi Reward và Score  
- 🟢🔴 Kiểm tra trạng thái Online/Offline  
- 📈 Tự động phát hiện thay đổi và gửi cảnh báo  
- 💾 Lưu trữ dữ liệu lịch sử node  
- 🔧 Dễ cấu hình và dễ triển khai  

---

## 📋 Yêu cầu hệ thống
- Python 3.7 trở lên  
- Kết nối mạng  
- Tài khoản Telegram  

---

## 🚀 Bắt đầu nhanh

### 1. Tạo Telegram Bot

#### Bước 1 — Tạo Bot
1. Mở Telegram, tìm **@BotFather**  
2. Gõ `/newbot`  
3. Đặt tên bot (VD: *Gensyn Monitor*)  
4. Đặt username bot (kết thúc bằng `bot`, ví dụ: `gensyn_monitor_bot`)  
5. Lấy **Bot Token**

#### Bước 2 — Lấy Chat ID
1. Nhắn `/start` cho bot vừa tạo  
2. Truy cập:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Tìm trường `"chat" -> "id"`  
4. Đây là **Chat ID** của bạn  

---

## 2. Chạy script thiết lập

```bash
python setup.py
```

Nhập theo hướng dẫn:
- **Bot Token**
- **Chat ID**
- **Thông tin Node** (ID hoặc name tuỳ cách dùng)

### ⚙️ Định dạng cấu hình Node

#### Cách 1 — Tên node (cũ):
```
loud sleek bat, knobby leaping kangaroo
```

#### Cách 2 — ID node + Ghi chú (khuyến nghị):
```
Qmb14s2E...x3nxxv7,Server A
QmPboLHe...EARMuavj,Server B
```

📌 *Sử dụng Peer ID để theo dõi chính xác hơn!*

---

## 3. Khởi động bot

```bash
python main.py
```

---

## 🧩 Các lệnh Telegram

| Lệnh | Mô tả |
|------|-------|
| `/start` | Hiển thị lời chào |
| `/status` | Lấy toàn bộ trạng thái node |
| `/help` | Hiển thị hướng dẫn |

---

## 📱 Ví dụ tin nhắn bot gửi

```
📊 Trạng thái Node (14:30:25)

1 🟢 loud sleek bat
R:78 | S:216 | ID:QmQR1...MW | R:75→78(+3) | S:210→216(+6)

2 🔴 knobby leaping kangaroo  
R:45 | S:120 | ID:QmX5R...KC | 🔴 Mới offline
```

---

## 📁 Cấu trúc file cấu hình

### Cấu hình mới:
```json
{
    "TELEGRAM_API_TOKEN": "",
    "CHAT_ID": "",
    "PEER_NAMES": [
        {
            "id": "Qmxxxx",
            "remark": "Server A"
        }
    ]
}
```

### Cấu hình cũ:
```json
{
    "PEER_NAMES": ["loud sleek bat"]
}
```

---

## 🛠️ Xử lý lỗi

### Node không đọc được JSON
```
json.decoder.JSONDecodeError
```
👉 Fix:
```bash
rm -f /root/GENSYNBOT/node_tasks.json
```

### Bot không phản hồi
- Kiểm tra bot có đang chạy không  
- Kiểm tra mạng  
- Kiểm tra Chat ID & Token  

---

## ⏱️ Chạy bot nền (khuyến nghị)
### Dùng screen
```bash
screen -S gensyn_bot
python main.py
# nhấn Ctrl+A rồi D để tách
```

### Dùng nohup
```bash
nohup python main.py > bot.log 2>&1 &
```

---

## 📦 File dữ liệu
| File | Mô tả |
|------|--------|
| `config.json` | Cấu hình bot |
| `node_tasks.json` | Lưu lịch sử Reward/Score/Online |

---

## ❤️ Ghi chú
- Luôn bảo vệ Bot Token và Chat ID  
- Khi node quá nhiều, nên dùng Peer ID để tăng độ chính xác  

---

Chúc bạn giám sát node **Gensyn** hiệu quả! ⚡
