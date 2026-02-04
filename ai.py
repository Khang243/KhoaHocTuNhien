import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64

# ==========================================
# 1. CẤU HÌNH API KEY
# ==========================================

# Key mặc định của bạn (đã mã hóa)
DEFAULT_API_ENCODED = "QUl6YVN5QVowb0pVMHJsMmhjV3RhdERWbG5wZFZYYU9nZ2p2ZDk0"
DEFAULT_KEY = base64.b64decode(DEFAULT_API_ENCODED).decode('utf-8')

# Giao diện nhập Key thủ công ở Sidebar
st.sidebar.title("Cấu hình")
user_key = st.sidebar.text_input("Nhập Gemini API Key của bạn (nếu key mặc định lỗi):", type="password")

# Ưu tiên sử dụng Key của người dùng nếu có, nếu không thì dùng Key mặc định
FINAL_API_KEY = user_key if user_key else DEFAULT_KEY

def get_optimal_model(api_key):
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["models/gemini-2.0-flash-exp", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
        for p in priority:
            if p in models: return p
        return models[0] if models else "models/gemini-1.5-flash"
    except Exception: 
        return "models/gemini-1.5-flash"

# Khởi tạo Model
SELECTED_MODEL = get_optimal_model(FINAL_API_KEY)

# ==========================================
# 2. GIAO DIỆN TỐI GIẢN
# ==========================================
st.set_page_config(page_title="Plant ID", page_icon="🌿")
st.title("🌿 Nhận Diện Tên Cây")

# Thông báo nếu hoàn toàn không có Key (trường hợp xóa cả key mặc định)
if not FINAL_API_KEY:
    st.warning("⚠️ Hiện không có API Key. Vui lòng nhập API Key ở thanh bên để bắt đầu.")
    st.stop()

source = st.radio("Nguồn:", ("Tải ảnh", "Camera"), horizontal=True)
image_input = st.file_uploader("Chọn ảnh", type=["jpg", "png"]) if source == "Tải ảnh" else st.camera_input("Chụp ảnh")

if image_input:
    img = Image.open(image_input)
    if st.button("XÁC ĐỊNH TÊN", use_container_width=True):
        with st.spinner('Đang phân tích...'):
            try:
                # Cấu hình lại với FINAL_API_KEY trước khi gọi model
                genai.configure(api_key=FINAL_API_KEY)
                model = genai.GenerativeModel(SELECTED_MODEL)
                
                prompt = "Chỉ trả về duy nhất 1 dòng văn bản theo định dạng: [Tên tiếng Việt] + [Tên khoa học]. Không thêm bất kỳ chữ nào khác."
                response = model.generate_content([prompt, img])
                
                st.success("Hoàn tất!")
                st.markdown(f"### Kết quả: `{response.text.strip()}`")
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.info("💡 Mẹo: Nếu lỗi liên quan đến API Key, hãy thử nhập Key cá nhân của bạn ở thanh bên trái.")