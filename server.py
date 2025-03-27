from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import edge_tts
import asyncio
import os
import io
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_ip_address():
    try:
        # Get the hostname
        hostname = socket.gethostname()
        # Get the IP address
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "127.0.0.1"

app = Flask(__name__)
CORS(app)

# Create output directory if it doesn't exist
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        text = request.json.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        voice = request.json.get('voice', "en-US-JennyNeural")
        logger.debug(f"Processing TTS request with text: {text[:50]}... using voice: {voice}")

        try:
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                audio_data = io.BytesIO()
                
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.write(chunk["data"])
                    elif chunk["type"] == "error":
                        raise Exception(chunk["data"].decode())
                
                audio_data.seek(0)
                return audio_data

            audio_stream = asyncio.run(generate_speech())
            return send_file(
                audio_stream,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name="speech.mp3"
            )

        except Exception as e:
            logger.error(f"Error in TTS endpoint: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        logger.error(f"Error in TTS endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/example', methods=['GET'])
def example():
    example_text = "Hello! This is an example of text to speech conversion using Microsoft Edge TTS."
    
    try:
        async def generate_speech():
            communicate = edge_tts.Communicate(example_text, "en-US-JennyNeural")
            audio_data = io.BytesIO()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
                elif chunk["type"] == "error":
                    raise Exception(chunk["data"].decode())
            
            audio_data.seek(0)
            return audio_data

        audio_stream = asyncio.run(generate_speech())
        return send_file(
            audio_stream,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="example.mp3"
        )

    except Exception as e:
        logger.error(f"Error in example endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting server...")
        # Change default port to 5001
        port = int(os.environ.get('PORT', 5001))
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"Port {port} is already in use. Try a different port:")
            logger.error("1. Change the port number in the code")
            logger.error("2. Or run with a different port: PORT=5002 python server.py")
        else:
            logger.error(f"Server failed to start: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)
