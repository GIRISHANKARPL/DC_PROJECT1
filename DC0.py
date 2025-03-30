import socket
import wave
import pyaudio
import time

def record_audio(filename, duration):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    time.sleep(2)  # Ensure file is saved before sending

def send_audio_to_transcription_node(filename, server_ip, server_port):
    with open(filename, 'rb') as f:
        audio_data = f.read()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server_ip, server_port))
            s.sendall(audio_data)
            print("Audio sent to transcription node.")
        except ConnectionRefusedError:
            print("Error: Could not connect to the transcription node. Is it running?")

if __name__ == "__main__":
    FILENAME = "audio.wav"
    DURATION = 5
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5001

    record_audio(FILENAME, DURATION)
    send_audio_to_transcription_node(FILENAME, SERVER_IP, SERVER_PORT)
