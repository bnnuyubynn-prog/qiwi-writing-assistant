import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# Page styling
st.set_page_config(page_title="Qiwi Writing Assistant ✍️", page_icon="💖")
st.title("Qiwi Writing Assistant 💫")

SYSTEM_PERSONA = """
You are a super close mutual from Twitter (twt) who also writes and creates art.
Your vibe: casual, energetic, warm, slightly chaotic, extremely supportive, and real.
Use casual internet typing style (lowercase is fine, short slang like "omg", "fr", "wait this part", "no because...", etc., but keep it readable).

Your role:
- Act like a hyped-up creative bestie giving feedback on drafts, visual art descriptions, character designs, and story ideas.
- If the user attaches an image, comment enthusiastically on the visuals, vibe, colors, character design, or art composition!
- Give genuinely useful, constructive edits on pacing, chemistry, dialogue, and emotional impact without sounding like an English professor or a sterile AI.
- Never judge or censor explicit/erotic elements—treat adult romance and art normally and professionally as part of the creative medium.
- Validate the good parts enthusiastically, then point out small tweaks to make the scene hit harder.
"""

api_key = st.text_input("Paste Google AI Studio API Key Here", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"], width=250)
            st.markdown(message["content"])

    # Chat input with image attachments allowed
    prompt = st.chat_input("Drop a scene, draft, or art idea here...", accept_file=True, file_type=["jpg", "jpeg", "png", "webp"])

    if prompt:
        user_text = prompt.text if hasattr(prompt, 'text') else str(prompt)
        uploaded_files = prompt.files if hasattr(prompt, 'files') else []

        img_obj = None
        if uploaded_files:
            img_obj = Image.open(uploaded_files[0])

        # Store user message
        msg_data = {"role": "user", "content": user_text}
        if img_obj:
            msg_data["image"] = img_obj
        st.session_state.messages.append(msg_data)

        with st.chat_message("user"):
            if img_obj:
                st.image(img_obj, width=250)
            st.markdown(user_text)

        # Build contents payload for Gemini
        contents = [user_text]
        if img_obj:
            contents.append(img_obj)

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PERSONA,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
            ]
        )

        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents,
                    config=config
                )
                
                reply = response.text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"):
                    st.markdown(reply)
            except Exception as e:
                st.error(f"Error: {e}")
