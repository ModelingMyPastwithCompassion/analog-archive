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

# העלמת התפריטים המובנים של פלטפורמת Streamlit למראה נקי לחלוטין
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# עיצוב אסתטי: רקע שחור עמוק ופונט קוד טהור (Consolas / Monaco)
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
    }
    html, body, [class*="css"], .stTextInput input, .stButton button {
        font-family: Consolas, Monaco, 'Courier New', Courier, monospace !important;
        color: #d3d3d3;
    }
    h1 {
        text-transform: uppercase;
        letter-spacing: 3px;
        border-bottom: 1px solid #333;
        padding-bottom: 15px;
    }
    .stTextInput input {
        background-color: #141414;
        color: #ffffff;
        border: 1px solid #333;
    }
    .stButton button {
        background-color: #1c1c1c;
        color: #ffffff;
        border: 1px solid #444;
    }
    .stButton button:hover {
        background-color: #333333;
        border-color: #666;
    }
</style>
""", unsafe_allow_html=True)

# הורדה אוטומטית של הזיפ מ-Google Drive וחילוצו
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

# UI Texts - המניפסט והכותרות האמנותיות
st.title("📼 Modeling My Past with Compassion")
st.markdown("""
*This engine is independently produced, its data sourced from 90s VHS tapes shot by my mother or father. The cinematography credit belongs to them. Using this raw technology, designed to preserve the original aesthetic, we can touch the memories of the past. The engine is built to simulate our memory: distorting, adding or subtracting details, and scrambling the sequence of events. Is this how it really was, or is this how I want to remember it?*

**Please treat these materials with compassion.**
""")

POLITE_WORDS = ["please", "thanks", "thank you", "love"]
STOP_WORDS = ["show", "me", "the", "a", "an", "and", "with", "in", "on", "of", "to", "is", "are"]

user_prompt = st.text_input("Enter Memory", value="")

# שמירת התמונה בזיכרון של Streamlit Session כדי שלא תיעלם בלחיצה על הורדה
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "download_bytes" not in st.session_state:
    st.session_state.download_bytes = None

if st.button("Dive Into"):
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

        size = 512

        if not matching_images:
            empty_frame = np.zeros((size, size, 3), dtype=np.uint8)
            noise = np.random.randint(0, 30, (size, size, 3), dtype=np.uint8)
            empty_frame = cv2.add(empty_frame, noise)
            cv2.putText(empty_frame, "MEMORY NOT FOUND IN ARCHIVE", (20, size // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2, cv2.LINE_AA)
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

        # --- הרולטה האסתטית ---
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

        shift = 4
        blended[:, :-shift, 2] = blended[:, shift:, 2]
        blended[:, shift:, 0] = blended[:, :-shift, 0]

        for i in range(0, size, 3):
            blended[i:i+1, :] = (blended[i:i+1, :] * 0.85).astype(np.uint8)

        kernel_x = cv2.getGaussianKernel(size, 250)
        kernel_y = cv2.getGaussianKernel(size, 250)
        kernel = kernel_y * kernel_x.T
        mask_vignette = kernel / kernel.max()
        mask_vignette = np.stack([mask_vignette]*3, axis=-1)
        blended = (blended * mask_vignette).astype(np.uint8)

        if not has_politeness:
            noise_overlay = np.random.randint(0, 120, (size, size, 3), dtype=np.uint8)
            blended = cv2.addWeighted(blended, 0.5, noise_overlay, 0.5, 0)
            cv2.putText(blended, "ACCESS DENIED:", (70, 230), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(blended, "COMPASSION PROTOCOL FAILED", (30, 270), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

        final_output = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
        st.session_state.generated_image = final_output
        
        # הכנה מראש של קובץ להורדה ושמירתו בזיכרון
        buf = io.BytesIO()
        Image.fromarray(final_output).save(buf, format="PNG")
        st.session_state.download_bytes = buf.getvalue()

# הצגת התמונה וכפתור ההורדה מתוך הזיכרון (כדי שלא ייעלמו בלחיצה)
if st.session_state.generated_image is not None:
    st.image(st.session_state.generated_image)
    
    if st.session_state.download_bytes is not None:
        st.download_button(
            label="Save this memory",
            data=st.session_state.download_bytes,
            file_name="analog_memory.png",
            mime="image/png"
        )
