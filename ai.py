import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64

# ==========================================
# 1. CẤU HÌNH API KEY & CSS
# ==========================================

# CSS để ẩn tên file sau khi upload
st.markdown("""
    <style>
    .st-emotion-cache-1erivf3.ex0cdbe0 {display: none;}
    .st-emotion-cache-1ky8h65 {display: none;}
    /* Ẩn caption mặc định của file uploader */
    div[data-testid="stFileUploaderFileName"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

DEFAULT_API_ENCODED = "QUl6YVN5QVowb0pVMHJsMmhjV3RhdERWbG5wZFZYYU9nZ2p2ZDk0"
DEFAULT_KEY = base64.b64decode(DEFAULT_API_ENCODED).decode('utf-8')

# Sidebar cho người dùng nhập key thủ công
st.sidebar.title("Cấu hình")
user_key = st.sidebar.text_input("Nhập Gemini API Key nếu lỗi:", type="password")
FINAL_API_KEY = user_key if user_key else DEFAULT_KEY

def get_optimal_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Thứ tự ưu tiên: 2.0 -> 1.5 Flash -> 1.5 Pro
        priority = ["models/gemini-2.0-flash-exp", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
        for p in priority:
            if p in models: return p
        return models[0] if models else "models/gemini-1.5-flash"
    except:
        return None
SELECTED_MODEL = get_optimal_model(FINAL_API_KEY)

# ==========================================
# 2. GIAO DIỆN NHẬN DIỆN
# ==========================================
st.set_page_config(page_title="Plant ID", page_icon="🌿")
st.title("🌿 Nhận Diện Tên Cây")

if not FINAL_API_KEY:
    st.warning("Vui lòng nhập API Key để bắt đầu.")
    st.stop()

source = st.radio("Nguồn:", ("Tải ảnh", "Camera"), horizontal=True)

# Widget upload/camera
if source == "Tải ảnh":
    image_input = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
else:
    image_input = st.camera_input("Chụp ảnh")

# Xử lý hiển thị ảnh và phân tích
if image_input:
    # 1. Hiển thị ảnh đã chọn/chụp
    img = Image.open(image_input)
    st.image(img, caption="Ảnh đang kiểm tra", use_container_width=True)
    
    # 2. Nút bấm xác định
    if st.button("XÁC ĐỊNH TÊN", use_container_width=True, type="primary"):
        with st.spinner('Đang phân tích...'):
            try:
                genai.configure(api_key=FINAL_API_KEY)
                model = genai.GenerativeModel(SELECTED_MODEL)
                
                prompt = "Chỉ trả về duy nhất 1 dòng văn bản theo định dạng: [Tên tiếng Việt] + [Tên khoa học]. Không thêm bất kỳ chữ nào khác."
                response = model.generate_content([prompt, img])
                
                st.success(f"**Kết quả:** {response.text.strip()}")
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.info("💡 Thử nhập API Key mới ở thanh bên trái nếu lỗi kết nối.")