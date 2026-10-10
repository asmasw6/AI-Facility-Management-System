import edge_tts
import uuid 
import os


async def text_to_speech(text: str):
    
    os.makedirs("audio_files", exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join("audio_files", filename)
    voice = "en-US-JennyNeural"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_path)
    return audio_path