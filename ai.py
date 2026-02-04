import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. CẤU HÌNH API KEY (ƯU TIÊN SECRET FILE)
# ==========================================
st.set_page_config(page_title="Plant ID - Pro", page_icon="🌿", layout="centered")

# Kiểm tra xem key có trong secrets.toml không
if "GEMINI_API_KEY" in st.secrets:
    active_api_key = st.secrets["GEMINI_API_KEY"]
    is_using_secret = True
else:
    active_api_key = None
    is_using_secret = False

with st.sidebar:
    st.title("⚙️ Cấu hình")
    
    if is_using_secret:
        st.success("✅ Đã tìm thấy API Key từ hệ thống.")
        # Cho phép người dùng ghi đè nếu họ muốn dùng key riêng
        override_key = st.text_input("Ghi đè API Key khác (nếu cần):", type="password")
        if override_key:
            active_api_key = override_key
    else:
        active_api_key = st.text_input("Nhập Gemini API Key của bạn:", type="password")
        st.info("Lấy Key tại: [aistudio.google.com](https://aistudio.google.com/)")
    
    st.divider()
    st.write("💡 **Mẹo:** Bạn có thể nhấn `Ctrl+V` vào ô tải file để dán ảnh trực tiếp.")

# Hàm tự động quét Model dựa trên Key
def get_optimal_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["models/gemini-2.0-flash-exp", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
        for p in priority:
            if p in models: return p
        return models[0] if models else "models/gemini-1.5-flash"
    except:
        return None

# ==========================================
# 2. GIAO DIỆN CHÍNH
# ==========================================
st.title("🌿 Nhận Diện Tên Cây")

if not active_api_key:
    st.warning("⚠️ Vui lòng cung cấp API Key để bắt đầu.")
else:
    SELECTED_MODEL = get_optimal_model(active_api_key)
    
    if SELECTED_MODEL:
        st.caption(f"🚀 Đang sử dụng Model: `{SELECTED_MODEL}`")
        
        image_input = st.file_uploader(
            "Kéo thả ảnh hoặc click rồi nhấn Ctrl+V để DÁN ảnh", 
            type=["jpg", "png", "jpeg"]
        )
        
        if not image_input and st.checkbox("Sử dụng Camera"):
            image_input = st.camera_input("Chụp ảnh lá")

        if image_input:
            img = Image.open(image_input)
            st.image(img, caption="Ảnh đang chờ phân tích", use_container_width=True)
            
            if st.button("🔍 XÁC ĐỊNH TÊN", use_container_width=True):
                try:
                    with st.spinner("Đang nhận diện..."):
                        model = genai.GenerativeModel(SELECTED_MODEL)
                        prompt = "Chỉ trả về đúng 1 dòng duy nhất: [Tên tiếng Việt] + [Tên khoa học]. Không thêm bất kỳ văn bản nào khác."
                        
                        response = model.generate_content([prompt, img])
                        result = response.text.strip()
                        
                        st.divider()
                        st.subheader(f"✨ Kết quả: {result}")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
    else:
        st.error("❌ Key không hợp lệ hoặc lỗi kết nối. Vui lòng kiểm tra lại.")