import socket
import speech_recognition as sr
import wave

def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        # Specify the language as Tamil (ta-IN)
        text = recognizer.recognize_google(audio, language="ta-IN")
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results. Check your internet connection."

def transcription_server(host, port, pos_node_ip, pos_node_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print("Transcription node listening on port", port)

        conn, addr = server_socket.accept()
        print("Connection received from", addr)

        audio_data = conn.recv(1024 * 1024)
        with open("received_audio.wav", "wb") as f:
            f.write(audio_data)

        # Transcribe the audio file
        transcription = transcribe_audio("received_audio.wav")
        print("Transcription completed:", transcription)

        # Send transcription to the POS tagging node
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pos_socket:
            pos_socket.connect((pos_node_ip, pos_node_port))
            pos_socket.sendall(transcription.encode())
            print("Transcription sent to POS tagging node.")

if __name__ == "__main__":
    HOST = "127.0.0.1"  # Host IP
    PORT = 5001  # Port to listen on
    POS_NODE_IP = "127.0.0.1"  # POS tagging node IP
    POS_NODE_PORT = 5002  # POS tagging node port

    transcription_server(HOST, PORT, POS_NODE_IP, POS_NODE_PORT)
