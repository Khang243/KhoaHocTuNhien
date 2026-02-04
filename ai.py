import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64

# ==========================================
# 1. CẤU HÌNH API KEY (KẾT NỐI VỚI SECRETS)
# ==========================================

# Kiểm tra xem Key có tồn tại trong st.secrets không
# if "GEMINI_API_KEY" in st.secrets:
#     GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
# else:
#     # Hiển thị thông báo nếu không tìm thấy key trong secrets
#     st.sidebar.warning("⚠️ Không tìm thấy Key trong Secrets.")
#     GEMINI_API_KEY = st.sidebar.text_input("Nhập API Key thủ công:", type="password")

API = ("QUl6YVN5QVowb0pVMHJsMmhjV3RhdERWbG5wZFZYYU9nZ2p2ZDk0")
GEMINI_API_KEY = base64.b64decode(API).decode('utf-8')
def get_optimal_model():
    if not GEMINI_API_KEY:
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Thứ tự ưu tiên model
        priority = ["models/gemini-2.0-flash-exp", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
        for p in priority:
            if p in models: return p
        return models[0] if models else "models/gemini-1.5-flash"
    except: 
        return "models/gemini-1.5-flash"

# Khởi tạo Model dựa trên kết quả quét
SELECTED_MODEL = get_optimal_model()

# ==========================================
# 2. GIAO DIỆN TỐI GIẢN
# ==========================================
st.set_page_config(page_title="Plant ID", page_icon="🌿")
st.title("🌿 Nhận Diện Tên Cây")

# Dừng app nếu hoàn toàn không có Key để tránh lỗi hệ thống
if not GEMINI_API_KEY:
    st.info("Vui lòng nhập API Key ở thanh bên để bắt đầu.")
    st.stop()

source = st.radio("Nguồn:", ("Tải ảnh", "Camera"), horizontal=True)
image_input = st.file_uploader("Chọn ảnh", type=["jpg", "png"]) if source == "Tải ảnh" else st.camera_input("Chụp ảnh")

if image_input:
    img = Image.open(image_input)
    if st.button("XÁC ĐỊNH TÊN", use_container_width=True):
        try:
            model = genai.GenerativeModel(SELECTED_MODEL)
            # Prompt yêu cầu AI trả về 1 dòng duy nhất
            prompt = "Chỉ trả về duy nhất 1 dòng văn bản theo định dạng: [Tên tiếng Việt] + [Tên khoa học]. Không thêm bất kỳ chữ nào khác."
            
            response = model.generate_content([prompt, img])
            
            # Hiển thị kết quả
            st.markdown(f"### Kết quả: `{response.text.strip()}`")
            
        except Exception as e:
            st.error(f"Lỗi: {e}")