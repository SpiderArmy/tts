import edge_tts
import asyncio
import os
import time
import subprocess

# Create output directory if it doesn't exist
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def list_voices():
    voices = await edge_tts.list_voices()
    return [voice["ShortName"] for voice in voices]

async def text_to_speech(text, voice="en-US-JennyNeural"):
    try:
        communicate = edge_tts.Communicate(text, voice)
        output_file = os.path.join(OUTPUT_DIR, f"speech_{int(time.time())}.mp3")
        
        print(f"Converting text to speech...")
        with open(output_file, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        print(f"Playing audio from {output_file}")
        # Use mpg123 to play the audio
        subprocess.run(['mpg123', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_file
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

async def main():
    # Get available voices
    voices = await list_voices()
    print("\nAvailable voices:")
    for i, voice in enumerate(voices):
        if voice.startswith("en-"):  # Only show English voices
            print(f"{i}: {voice}")
    
    # Get user input
    text = input("\nEnter the text you want to convert to speech: ")
    # text = (enter text here)
    voice_choice = input("Enter voice (press Enter for default en-US-JennyNeural): ")
    
    # Use selected voice or default
    selected_voice = voices[int(voice_choice)] if voice_choice.isdigit() else "en-US-JennyNeural"
    
    # Convert and play
    await text_to_speech(text, selected_voice)

if __name__ == "__main__":
    asyncio.run(main())
