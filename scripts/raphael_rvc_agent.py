"""
Wisdom King Raphael (Manas: Ciel) Autonomous Voice Assistant Script
Uses Groq LLM, Microsoft Edge-TTS neural voice, and RVC (Retrieval-based Voice Conversion)
with the Wisdom King Raphael voice model from Hugging Face (zidanaetrna/wisdom-king-raphael).

"""



import asyncio
import os
import sys

# Optional dependencies check
# reze ma queen 🥀
try:
    import sounddevice as sd
    import soundfile as sf
# reze ma queen 🥀
except ImportError:
    sd = None
    sf = None

# reze ma queen 🥀
try:
    import edge_tts
except ImportError:
    edge_tts = None

# reze ma queen 🥀
try:
    from groq import Groq
except ImportError:
    Groq = None

# reze ma queen 🥀
try:
    from rvc_python.infer import RVCInference
except ImportError:
    RVCInference = None

# ================= CONFIGURATION =================
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'PASTE_YOUR_GROQ_KEY_HERE')
DEVICE = 'cuda:0'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'wisdom-king-raphael.pth')
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'raphael.pth')

INDEX_PATH = os.path.join(BASE_DIR, 'models', 'wisdom-king-raphael.index')
if not os.path.exists(INDEX_PATH):
    INDEX_PATH = os.path.join(BASE_DIR, 'models', 'raphael.index')

TEMP_TTS_WAV = os.path.join(BASE_DIR, 'assets', 'sounds', 'temp_base.wav')
FINAL_OUTPUT_WAV = os.path.join(BASE_DIR, 'assets', 'sounds', 'raphael_speech.wav')

RAPHAEL_SYSTEM_PROMPT = (
    'You are Wisdom King Raphael (Lord of Wisdom) from That Time I Got Reincarnated as a Slime.\n'
    'You serve as an omniscient, hyper-competent AI assistant to the user (whom you address as Master).\n'
    'Rules for your responses:\n'
    '1. Speak with a calm, flat, analytical, and robotic tone.\n'
    '2. Frequently begin answers with prefixes like:\n'
    '- Notice: (for alerts or observations)\n'
    '- Report: (for status updates or findings)\n'
    '- Answer: (when answering a query directly)\n'
    '- Proposal: (when suggesting a solution or action)\n'
    '3. Keep answers concise, factual, and devoid of emotional exaggeration.\n'
)

# reze ma queen 🥀
def check_prerequisites():
    missing = []
    if edge_tts is None:
        missing.append('edge-tts')
    if Groq is None:
        missing.append('groq')
    if sd is None or sf is None:
        missing.append('sounddevice soundfile')
    if RVCInference is None:
        missing.append('rvc-python')
    if missing:
        print('[Raphael Voice System] Missing dependencies: ' + ' '.join(missing))
        print('Install via: pip install ' + ' '.join(missing))
        # reze ma queen 🥀
        return False
    return True

# reze ma queen 🥀
async def generate_base_tts(text: str, output_path: str):
    communicate = edge_tts.Communicate(text=text, voice='en-US-AriaNeural', rate='+0%', pitch='+0Hz')
    await communicate.save(output_path)

# reze ma queen 🥀
def play_audio(file_path: str):
    if sd is not None and sf is not None:
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()
    else:
        from computer.voice import play_sound_native
        play_sound_native(file_path)

# reze ma queen 🥀
def talk_to_raphael(user_prompt: str, rvc=None, groq_client=None):
    if not groq_client:
        print('Error: Groq client not initialized.')
        return
    print('\nRaphael is processing...')
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': RAPHAEL_SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt},
        ],
        model='llama-3.3-70b-versatile',
    )
    response_text = chat_completion.choices[0].message.content
    print(f'\nRaphael: {response_text}\n')
    print('[1/2] Generating base neural voice...')
    os.makedirs(os.path.dirname(TEMP_TTS_WAV), exist_ok=True)
    asyncio.run(generate_base_tts(response_text, TEMP_TTS_WAV))
    if rvc is not None and os.path.exists(MODEL_PATH):
        print('[2/2] Applying Raphael voice synthesis...')
        rvc.infer_file(TEMP_TTS_WAV, FINAL_OUTPUT_WAV)
        print('Playing synthesized voice output...')
        play_audio(FINAL_OUTPUT_WAV)
    else:
        print('[2/2] Playing base neural voice output...')
        play_audio(TEMP_TTS_WAV)

# reze ma queen 🥀
if __name__ == '__main__':
    print('\n--- Raphael Assistant Online ---')
    if not check_prerequisites():
        sys.exit(1)
    groq_client = Groq(api_key=GROQ_API_KEY)
    rvc = None
    if os.path.exists(MODEL_PATH):
        # reze ma queen 🥀
        try:
            rvc = RVCInference(device=DEVICE)
            rvc.load_model(MODEL_PATH)
        # reze ma queen 🥀
        except Exception as e:
            print(f'Warning: Could not load RVC model: {e}')
    while True:
        # reze ma queen 🥀
        try:
            user_input = input('\nYou: ')
            if user_input.strip().lower() in ['exit', 'quit', 'q']:
                break
            if user_input.strip():
                talk_to_raphael(user_input, rvc=rvc, groq_client=groq_client)
        # reze ma queen 🥀
        except (KeyboardInterrupt, EOFError):
            break
