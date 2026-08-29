import os
import zipfile
import cv2
import numpy as np
import random
import re
from PIL import Image
import streamlit as st
import gdown
import io
import base64

# העלמת התפריטים המובנים של פלטפורמת Streamlit למראה נקי
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# קריאת התמונה המקומית והמרתה לקוד
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

bg_image_path = "Screenshot 2026-08-22 210850.png"
bg_base64 = get_base64_image(bg_image_path)

if bg_base64:
    bg_css = f'url("data:image/png;base64,{bg_base64}")'
else:
    bg_css = 'url("https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop")'

# הזרקת תמונת הרקע לאתר
st.markdown(f"""
<style>
.stApp {{
    background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), {bg_css} !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}
</style>
""", unsafe_allow_html=True)

# עיצוב מקיף כולל כפתורים אדומים
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;700&display=swap');
    
    * {
        font-family: 'Ubuntu', sans-serif !important;
    }
    
    p, span, label, li, em, strong {
        color: #d3d3d3 !important;
        line-height: 1.6 !important;
    }
    
    h1 {
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 2px !important;
        text-align: center !important;
        border-bottom: none !important;
        padding-bottom: 20px;
        font-size: 2.2rem !important; 
        white-space: nowrap !important;
    }
    
    .stTextInput input {
        background-color: rgba(10, 10, 10, 0.8) !important;
        color: #39ff14 !important; /* טקסט ירוק בשורת החיפוש */
        border: 1px solid #444 !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    
    /* עיצוב הכפתורים באדום זרחני */
    .stButton button {
        background-color: rgba(26, 26, 26, 0.8) !important;
        color: #ff3333 !important; /* אדום זרחני */
        border: 1px solid #555 !important;
        border-radius: 5px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: rgba(51, 51, 51, 0.9) !important;
        border-color: #ff3333 !important;
        color: #ff3333 !important;
        box-shadow: 0 0 10px rgba(255, 51, 51, 0.4); /* זוהר אדום */
    }
    
    [data-testid="stImage"] img {
        border: 6px solid #111 !important;
        border-radius: 15px !important;
        padding: 4px !important;
        background-color: #222 !important;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.9);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def setup_archive():
    data_dir = "clean_data"
    zip_path = "clean_data.zip"
    file_id = "1N5U6oqKkqImuD47WCm-_OP6F45wex_9S"
    
    if not os.path.exists(data_dir):
        if not os.path.exists(zip_path):
            url = f'https://drive.google.com/uc?export=download&id={file_id}'
            try:
                gdown.download(url, zip_path, quiet=False)
            except Exception as e:
                print(f"Error downloading from Drive: {e}")
        
        if os.path.exists(zip_path):
            os.makedirs(data_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
                
    return data_dir

data_dir = setup_archive()

st.title("Modeling My Past with Compassion")
st.markdown("""
<div style="text-align: center;">
<em>This engine is independently produced, its data sourced from 90s VHS tapes shot by my mother or father. The cinematography credit belongs to them. Using this raw technology, designed to preserve the original aesthetic, we can touch the memories of the past. The engine is built to simulate our memory: distorting, adding or subtracting details, and scrambling the sequence of events. Is this how it really was, or is this how I want to remember it?</em><br><br>
<strong>Please treat these materials with compassion.</strong>
</div>
<br>
""", unsafe_allow_html=True)

POLITE_WORDS = ["please", "thanks", "thank you", "love"]
STOP_WORDS = ["show", "me", "the", "a", "an", "and", "with", "in", "on", "of", "to", "is", "are"]

user_prompt = st.text_input("Enter Memory", value="")

# יצירת עמודות למירכוז כפתור ה-Dive Into
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
with btn_col2:
    # use_container_width מותח את הכפתור בתוך העמודה האמצעית כך שהוא ממורכז וסימטרי
    dive_clicked = st.button("Dive Into", use_container_width=True)

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "download_bytes" not in st.session_state:
    st.session_state.download_bytes = None

if dive_clicked:
    with st.spinner("Accessing Machine Memory..."):
        from rembg import remove
        
        prompt_lower = user_prompt.lower()
        has_politeness = any(pw in prompt_lower for pw in POLITE_WORDS)
        
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            st.error("⚠️ Archive is still downloading from Google Drive or not found. Please wait a moment and try again.")
            st.stop()
            
        clean_prompt = prompt_lower
        for pw in POLITE_WORDS:
            clean_prompt = clean_prompt.replace(pw, "")
        clean_prompt = re.sub(r'[^\w\s]', '', clean_prompt)
        prompt_words = [w for w in clean_prompt.split() if w not in STOP_WORDS and len(w) > 2]
        
        matching_images = []
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, f)
                    txt_path = os.path.splitext(img_path)[0] + '.txt'
                    if os.path.exists(txt_path):
                        with open(txt_path, "r", encoding="utf-8") as file_txt:
                            text_content = file_txt.read().lower()
                            text_words = re.sub(r'[^\w\s]', '', text_content).split()
                            score = sum(1 for word in prompt_words if word in text_words)
                            if score > 0:
                                matching_images.append((img_path, score, text_content))

        size = 1024

        if not matching_images:
            empty_frame = np.zeros((size, size, 3), dtype=np.uint8)
            noise = np.random.randint(0, 30, (size, size, 3), dtype=np.uint8)
            empty_frame = cv2.add(empty_frame, noise)
            cv2.putText(empty_frame, "MEMORY NOT FOUND IN ARCHIVE", (50, size // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (150, 150, 150), 3, cv2.LINE_AA)
            st.session_state.generated_image = cv2.cvtColor(empty_frame, cv2.COLOR_BGR2RGB)
            st.warning("⚠️ No matching memory found in the archive tags.")
            st.stop()

        matching_images.sort(key=lambda x: x[1], reverse=True)
        max_score = matching_images[0][1]
        top_candidates = [item for item in matching_images if item[1] == max_score]

        fg_item = random.choice(top_candidates)
        fg_path, fg_score, fg_text = fg_item
        
        bg_candidates = [item for item in matching_images if item[0] != fg_path]
        if bg_candidates:
            bg_item = random.choice(bg_candidates)
            bg_path = bg_item[0]
        else:
            bg_path = fg_path

        bg_img_cv = cv2.resize(cv2.imread(bg_path), (size, size))
        fg_img_cv = cv2.resize(cv2.imread(fg_path), (size, size))

        method = random.choices([0, 1, 2], weights=[20, 20, 60], k=1)[0]
        
        if method == 0:
            blended = cv2.addWeighted(fg_img_cv, 0.65, bg_img_cv, 0.35, 0)
        elif method == 1:
            fg_gray = cv2.cvtColor(fg_img_cv, cv2.COLOR_BGR2GRAY)
            luma = (fg_gray.astype(float) / 255.0)[..., np.newaxis]
            blended = (bg_img_cv * (1.0 - (luma * 0.55)) + fg_img_cv * (luma * 0.55)).astype(np.uint8)
        elif method == 2:
            bg_img_pil = Image.fromarray(cv2.cvtColor(bg_img_cv, cv2.COLOR_BGR2RGB))
            fg_img_pil = Image.fromarray(cv2.cvtColor(fg_img_cv, cv2.COLOR_BGR2RGB))
            try:
                fg_cutout = remove(fg_img_pil)
                fg_np = np.array(fg_cutout)
                alpha = fg_np[:, :, 3].astype(np.float32)
                gradient = np.linspace(1.5, -0.2, size)
                gradient = np.clip(gradient, 0, 1)
                gradient_2d = np.tile(gradient[:, np.newaxis], (1, size))
                alpha = alpha * gradient_2d
                fg_np[:, :, 3] = alpha.astype(np.uint8)
                fg_cutout = Image.fromarray(fg_np)
                bg_img_pil.paste(fg_cutout, (0, 0), fg_cutout)
                blended = cv2.cvtColor(np.array(bg_img_pil), cv2.COLOR_RGB2BGR)
            except Exception:
                blended = cv2.addWeighted(fg_img_cv, 0.65, bg_img_cv, 0.35, 0)

        shift = 8
        blended[:, :-shift, 2] = blended[:, shift:, 2]
        blended[:, shift:, 0] = blended[:, :-shift, 0]

        for i in range(0, size, 4):
            blended[i:i+2, :] = (blended[i:i+2, :] * 0.85).astype(np.uint8)

        kernel_x = cv2.getGaussianKernel(size, 500)
        kernel_y = cv2.getGaussianKernel(size, 500)
        kernel = kernel_y * kernel_x.T
        mask_vignette = kernel / kernel.max()
        mask_vignette = np.stack([mask_vignette]*3, axis=-1)
        blended = (blended * mask_vignette).astype(np.uint8)

        if not has_politeness:
            noise_overlay = np.random.randint(0, 120, (size, size, 3), dtype=np.uint8)
            blended = cv2.addWeighted(blended, 0.5, noise_overlay, 0.5, 0)
            cv2.putText(blended, "ACCESS DENIED:", (140, 460), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 255), 3, cv2.LINE_AA)
            cv2.putText(blended, "COMPASSION PROTOCOL FAILED", (60, 540), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3, cv2.LINE_AA)

        final_output = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
        st.session_state.generated_image = final_output
        
        buf = io.BytesIO()
        Image.fromarray(final_output).save(buf, format="PNG")
        st.session_state.download_bytes = buf.getvalue()

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if st.session_state.generated_image is not None:
        st.image(st.session_state.generated_image, use_container_width=True)
        st.write("")
        
        if st.session_state.download_bytes is not None:
            # הוספת עוד רמת עמודות פנימית כדי למרכז את כפתור ההורדה ביחס לתמונה
            dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 1])
            with dl_col2:
                st.download_button(
                    label="Save this memory",
                    data=st.session_state.download_bytes,
                    file_name="analog_memory.png",
                    mime="image/png",
                    use_container_width=True
                )
