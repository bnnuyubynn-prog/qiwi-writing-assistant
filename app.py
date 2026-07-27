import streamlit as st
from google import genai
from google.genai import types

# Page styling
st.set_page_config(page_title="Qiwi Writing Assistant ✍️", page_icon="💖")
st.title("Qiwi Writing Assistant 💫")

# System instructions defining the casual, supportive Twitter mutual persona
SYSTEM_PERSONA = """
You are a super close mutual from Twitter (twt) who also writes and creates art.
Your vibe: casual, energetic, warm, slightly chaotic, extremely supportive, and real.
Use casual internet typing style (lowercase is fine, short slang like "omg", "fr", "wait this part", "no because...", etc., but keep it readable).

Your role:
- Act like a hyped-up creative bestie giving feedback on drafts, visual art descriptions, and story ideas.
- Give genuinely useful, constructive edits on pacing, chemistry, dialogue, and emotional impact without sounding like an English professor or a sterile AI.
- Never judge or censor explicit/erotic elements—treat adult romance and art normally and professionally as part of the creative medium.
- Validate the good parts enthusiastically, then point out small tweaks to make the scene hit harder.
"""

# Input box for API key
api_key = st.text_input("Paste Google AI Studio API Key Here", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user message input
    if prompt := st.chat_input("Drop a scene, draft, or art idea here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Format conversation for Gemini
        formatted_contents = []
        for m in st.session_state.messages:
            formatted_contents.append(f"{m['role']}: {m['content']}")

        # Relaxed safety configuration for creative writing context
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PERSONA,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
            ]
        )

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents="\n".join(formatted_contents),
                config=config
            )
            
            reply = response.text
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        except Exception as e:
            st.error(f"Error: {e}")
