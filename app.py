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

# העלמת התפריטים המובנים והסתרת קישורי הכותרות
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
h1 a, h2 a, h3 a, .st-emotion-cache-1vt4ygl {
    display: none !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# קריאת קבצים מקומיים בלבד (פרטיות מלאה ללא CDN)
@st.cache_data
def load_base64_media(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    return ""

# ==========================================
# טעינת קבצי מדיה מראש (GIF, תמונה וסאונד)
# ==========================================

mixer_gif_path = "analogmixer.gif"
mixer_base64 = load_base64_media(mixer_gif_path)

surreal_gif_path = "surrealroom.gif"
surreal_base64 = load_base64_media(surreal_gif_path)

bg_image_path = "Screenshot 2026-08-22 210850.png"
bg_base64 = load_base64_media(bg_image_path)

audio_file_path = "VTS_01_2-[AudioTrimmer.com].mp3"
audio_base64 = load_base64_media(audio_file_path)

audio_no_path = "VTS_01_4-[AudioTrimmer.com].mp3"
audio_no_base64 = load_base64_media(audio_no_path)

def inject_gif_bg(base64_gif):
    if base64_gif:
        gif_css = f'url("data:image/gif;base64,{base64_gif}")'
        st.markdown(f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), {gif_css} !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background: #0a0a0a !important; }</style>", unsafe_allow_html=True)

def inject_image_bg(base64_img):
    if base64_img:
        bg_css = f'url("data:image/png;base64,{base64_img}")'
        st.markdown(f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), {bg_css} !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        </style>
        """, unsafe_allow_html=True)

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
        position: relative;
        z-index: 10;
        text-shadow: 2px 2px 15px rgba(0,0,0,1);
    }
    
    .stTextInput input {
        background-color: rgba(10, 10, 10, 0.8) !important;
        color: #39ff14 !important;
        border: 1px solid #444 !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    
    .stButton button {
        background-color: rgba(26, 26, 26, 0.8) !important;
        color: #ff3333 !important;
        border: 1px solid #555 !important;
        border-radius: 5px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold !important;
        transition: all 0.3s ease;
        position: relative;
        z-index: 10;
    }
    
    .stButton button:hover {
        background-color: rgba(51, 51, 51, 0.9) !important;
        border-color: #ff3333 !important;
        color: #ff3333 !important;
        box-shadow: 0 0 10px rgba(255, 51, 51, 0.4);
    }
    
    [data-testid="stImage"] img {
        border: 6px solid #111 !important;
        border-radius: 15px !important;
        padding: 4px !important;
        background-color: #222 !important;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.9);
    }

    @media (max-width: 768px) {
        h1 {
            font-size: 1.4rem !important;
            white-space: normal !important;
            line-height: 1.3 !important;
            padding-bottom: 10px;
        }
        
        .stMarkdown div {
            font-size: 0.9rem !important;
        }
        
        [data-testid="stImage"] img {
            border: 3px solid #111 !important;
            padding: 2px !important;
            border-radius: 10px !important;
        }
        
        .stTextInput {
            width: 100% !important;
        }
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

if "human_status" not in st.session_state:
    st.session_state.human_status = "pending"

# ==========================================
# מסך 1: שער הכניסה
# ==========================================
if st.session_state.human_status == "pending":
    inject_gif_bg(mixer_base64)
    
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>DO YOU FEEL HUMAN?</h1>", unsafe_allow_html=True)
    st.write("")
    
    audio_intro_path = "INTRO_AUDIO.mp3"
    audio_intro_base64 = load_base64_media(audio_intro_path)
    if audio_intro_base64:
        intro_audio_html = f"""
            <div style="text-align: center; max-width: 300px; margin: 0 auto; margin-bottom: 20px; position: relative; z-index: 10;">
            <audio controls>
            <source src="data:audio/mp3;base64,{audio_intro_base64}" type="audio/mpeg">
            </audio>
            </div>
            """
        st.markdown(intro_audio_html, unsafe_allow_html=True)

    st.write("")
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
    with col2:
        if st.button("YES", use_container_width=True):
            st.session_state.human_status = "yes"
            st.rerun()
    with col4:
        if st.button("NO", use_container_width=True):
            st.session_state.human_status = "no"
            st.rerun()

# ==========================================
# מסך 2: תשובה שלילית (NO)
# ==========================================
elif st.session_state.human_status == "no":
    inject_gif_bg(surreal_base64)
    
    if audio_no_base64:
        audio_html = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{audio_no_base64}" type="audio/mpeg">
            </audio>
            """
        st.markdown(audio_html, unsafe_allow_html=True)
        
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #ff3333 !important;'>ACCESS RESTRICTED</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; position: relative; z-index: 10; text-shadow: 2px 2px 10px black;">
    <strong>Come back anytime</strong><br>
    <em>when you feel more human.</em>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("GO BACK", use_container_width=True):
            st.session_state.human_status = "pending"
            st.rerun()

# ==========================================
# מסך 4: הצהרת כוונות טכנית (ABOUT)
# ==========================================
elif st.session_state.human_status == "about":
    inject_image_bg(bg_base64)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1>SYSTEM PROTOCOL</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(10, 10, 10, 0.85); padding: 30px; border-radius: 10px; border: 1px solid #444; position: relative; z-index: 10; text-align: left;">
    <h3 style="color: #ff3333 !important; text-transform: uppercase; margin-bottom: 10px; font-size: 1.2rem;">Architectural Independence</h3>
    <p>This memory engine was built from scratch as an alternative to commercial AI systems. It does not transmit data to corporate servers nor does it rely on them for real-time processing; instead, it is based on local code processing a private archive.</p>
    <p>There is no use of commercial image generators trained on copyrighted materials scraped from the internet without permission. This machine is strictly material—it distorts and reconstructs only the personal raw materials I fed into it.</p>
    <p>To build this independent system, I utilized tools and infrastructures from the world's largest corporations. The difference lies between relying on their tools for construction, and subjugating the data and the creation to their engines. The raw materials that make up this machine include:</p>
    
    <ul style="margin-top: 15px;">
        <li><strong>Hardware:</strong> A Dell computer powered by Intel processors.</li>
        <li><strong>Cloud Infrastructure & Storage:</strong> The source code is hosted on GitHub (owned by Microsoft), the archive is pulled from Google Drive, and the interface is hosted on Streamlit servers.</li>
        <li><strong>Open Source:</strong> Image processing and memory glitches are executed using the OpenCV math library, and background extraction is performed locally through an open model called Rembg (independent of any external server).</li>
        <li><strong>Preparation Assistance:</strong> The initial text tagging of the archive was previously done by the BLIP model, and the system's code was developed and written through a dialogue with Google's Gemini language model. Additionally, free online tools like AudioTrimmer were used for sound editing.</li>
        <li><strong>Independent Semantic Mapping:</strong> To bypass the language constraints of commercial automated models, prompt matching is executed through an independent synonym matrix that I built manually.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("RETURN TO ENGINE", use_container_width=True):
            st.session_state.human_status = "yes"
            st.rerun()

# ==========================================
# מסך 3: המנוע עצמו
# ==========================================
elif st.session_state.human_status == "yes":
    inject_image_bg(bg_base64)
    
    st.title("Modeling My Past with Compassion")
    st.markdown("""
    <div style="text-align: center; position: relative; z-index: 10;">
    <em>This engine is a personal archive, constructed from fragments of VHS tapes shot by my parents throughout the 90s. The cinematography belongs to them. Built as a closed, independent protocol, free from commercial extraction, it merges this analog footage with synthetic processes to simulate how human memory actually works: distorting, adding or subtracting details, and scrambling the timeline. Is this how it really happened, or is this simply how I choose to remember it?</em><br><br>
    <strong>Please treat these materials with compassion.</strong>
    </div>
    <br>
    """, unsafe_allow_html=True)

    POLITE_WORDS = ["please", "thanks", "thank you", "love"]
    STOP_WORDS = ["show", "me", "the", "a", "an", "and", "with", "in", "on", "of", "to", "is", "are"]

    SYNONYM_MAP = {
        "cat": ["cat", "kitten", "pet", "animal", "feline", "jasper", "חתול"],
        "woman": ["woman", "mother", "mom", "female", "lady", "person", "girl", "אמא", "אישה"],
        "man": ["man", "father", "dad", "male", "guy", "person", "אבא", "גבר"],
        "dog": ["dog", "puppy", "pet", "animal", "canine", "כלב"],
        "house": ["house", "home", "room", "indoor", "building", "בית", "חדר"],
        "sea": ["sea", "ocean", "water", "beach", "coast", "ים", "חוף"],
        "car": ["car", "vehicle", "drive", "road", "רכב", "אוטו"]
    }

    user_prompt = st.text_input("Enter Memory", value="")

    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col2:
        dive_clicked = st.button("Dive In", use_container_width=True)

    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    if "download_bytes" not in st.session_state:
        st.session_state.download_bytes = None

    if dive_clicked:
        if audio_base64:
            audio_html = f"""
                <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                </audio>
                """
            st.markdown(audio_html, unsafe_allow_html=True)

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
            
            base_words = [w for w in clean_prompt.split() if w not in STOP_WORDS and len(w) > 1]
            
            expanded_words = set(base_words)
            for word in base_words:
                for key, synonyms in SYNONYM_MAP.items():
                    if word == key or word in synonyms:
                        expanded_words.update(synonyms)
            
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
                                
                                score = sum(1 for word in expanded_words if word in text_words)
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
                dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 1])
                with dl_col2:
                    st.download_button(
                        label="Save this memory",
                        data=st.session_state.download_bytes,
                        file_name="analog_memory.png",
                        mime="image/png",
                        use_container_width=True
                    )

    # כפתור מעבר למסך ההצהרה הטכנית בתחתית מנוע החיפוש
    st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
    manifesto_col1, manifesto_col2, manifesto_col3 = st.columns([1, 1, 1])
    with manifesto_col2:
        if st.button("SYSTEM PROTOCOL", use_container_width=True):
            st.session_state.human_status = "about"
            st.rerun()
