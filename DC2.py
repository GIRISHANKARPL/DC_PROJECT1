import socket
import stanza

# Load the Tamil NLP model (Ensure it's downloaded)
try:
    nlp = stanza.Pipeline('ta', processors='tokenize,pos', use_gpu=False)
except:
    stanza.download('ta')
    nlp = stanza.Pipeline('ta', processors='tokenize,pos', use_gpu=False)

# Mapping Stanza POS tags to Tamil labels
POS_TAGS_TAMIL = {
    'NOUN': 'பெயர்ச்சொல்',
    'VERB': 'வினைச்சொல்',
    'AUX': 'வினைச்சொல்',  
    'ADJ': 'விளிப்புச் சொல்',
    'PRON': 'சரிகைச்சொல்',
    'CONJ': 'இணைப்புச் சொல்',
    'DET': 'துணைமொழிச் சொல்',
    'ADP': 'பின்னிடைச்சொல்',
    'PROPN': 'கூற்று பெயர்',  # Proper noun
    'NUM': 'எண்ணுப்பெயர்',
    'PART': 'இடைச்சொல்',
    'SYM': 'சின்னம்',
    'X': 'தெரியாத சொல்'
}

# List of Tamil words that are proper nouns but might be misclassified
KNOWN_PROPER_NOUNS = {"குரு", "தமிழ்", "சென்னை", "இந்தியா"}  # Add more as needed

def tag_with_stanza(text):
    """Uses Stanza to tokenize and POS tag Tamil text."""
    doc = nlp(text)
    pos_tags = []
    
    for sentence in doc.sentences:
        for word in sentence.words:
            original_tag = word.upos  # Stanza's Universal POS tag
            
            # Special handling for known proper nouns
            if word.text in KNOWN_PROPER_NOUNS:
                tamil_tag = 'கூற்று பெயர்'  # Proper noun
            elif original_tag == 'PROPN':
                tamil_tag = 'கூற்று பெயர்'  # General proper noun mapping
            elif original_tag == 'ADV':
                tamil_tag = 'காலவிசேஷம்' if word.text in ["இன்று", "நேற்று", "நாளை"] else 'கிரியைவிசேஷம்'
            else:
                tamil_tag = POS_TAGS_TAMIL.get(original_tag, 'தெரியாத சொல்')  # Default mapping

            pos_tags.append((word.text, tamil_tag))
            print(f"Word: {word.text}, Stanza POS: {original_tag}, Mapped POS: {tamil_tag}")  
    
    return pos_tags

def pos_tagging_server(host, port, coordinator_ip, coordinator_port):
    """Server that receives transcribed text, performs POS tagging, and sends results to the coordinator."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"POS tagging node listening on {host}:{port}")

        conn, addr = server_socket.accept()
        print("Connection received from", addr)

        # Receive transcription data
        transcription = b''
        while True:
            data = conn.recv(1024)
            if not data:
                break
            transcription += data
        transcription = transcription.decode().strip()

        print("Received transcription:", transcription)

        # Perform POS tagging
        try:
            pos_tags = tag_with_stanza(transcription)
            print("POS tagging completed:", pos_tags)
        except Exception as e:
            print(f"Error during POS tagging: {e}")
            pos_tags = []

        # Send POS tags to coordinator
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as coord_socket:
            try:
                coord_socket.connect((coordinator_ip, coordinator_port))
                coord_socket.sendall(str(pos_tags).encode())
                print("POS tags sent to coordinator.")
            except Exception as e:
                print(f"Error sending POS tags to coordinator: {e}")

if __name__ == "__main__":
    HOST = "127.0.0.1"  
    PORT = 5002  
    COORDINATOR_IP = "127.0.0.1"  
    COORDINATOR_PORT = 5003  

    pos_tagging_server(HOST, PORT, COORDINATOR_IP, COORDINATOR_PORT)
