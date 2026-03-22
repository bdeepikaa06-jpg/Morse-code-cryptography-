import numpy as np
import scipy.io.wavfile as wav
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import getpass

# Dictionary representing the Morse code chart
MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
                   'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
                   'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
                   'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
                   'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
                   'Z': '--..', '1': '.----', '2': '..---', '3': '...--', 
                   '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
                   '8': '---..', '9': '----.', '0': '-----', ',': '--..--', 
                   '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', 
                   '(': '-.--.', ')': '-.--.-'}

# Dictionary representing the Morse code chart (reversed)
REVERSED_MORSE_CODE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}

# Function to convert text to Morse code
def text_to_morse(text):
    morse_code = ""
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            morse_code += MORSE_CODE_DICT[char] + ' '
        else:
            morse_code += ' '
    return morse_code

# Function to generate audio signal for dot
def generate_dot(duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * 440 * t)

# Function to generate audio signal for dash
def generate_dash(duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * 440 * t)

# Function to generate Morse code audio
def generate_morse_audio(morse_code):
    dot_duration = 0.1
    dash_duration = 3 * dot_duration

    audio_signal = []
    for symbol in morse_code:
        if symbol == '.':
            audio_signal.extend(generate_dot(dot_duration))
        elif symbol == '-':
            audio_signal.extend(generate_dash(dash_duration))
        elif symbol == ' ':
            audio_signal.extend(np.zeros(int(dot_duration * 44100)))

    audio_signal = np.array(audio_signal, dtype=np.float32)
    return audio_signal

# Function to save audio signal to file
def save_audio_to_file(audio_signal, filename):
    wav.write(filename, 44100, audio_signal)

# Function to generate a hashed password
def generate_hashed_password(password):
    return hashlib.sha256(password.encode()).digest()

# Function to encrypt the Morse code message
def encrypt_morse_code(morse_code, encryption_key):
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    encrypted_morse_code = cipher.iv + cipher.encrypt(pad(morse_code.encode(), AES.block_size))
    return encrypted_morse_code

# Function to decrypt the encrypted Morse code message
def decrypt_morse_code(encrypted_morse_code, encryption_key):
    iv = encrypted_morse_code[:AES.block_size]
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv=iv)
    decrypted_morse_code = unpad(cipher.decrypt(encrypted_morse_code[AES.block_size:]), AES.block_size)
    return decrypted_morse_code.decode()

# Function to convert Morse code to text
def morse_to_text(morse_code):
    text = ""
    morse_words = morse_code.split('   ')
    for morse_word in morse_words:
        morse_chars = morse_word.split(' ')
        for morse_char in morse_chars:
            if morse_char in REVERSED_MORSE_CODE_DICT:
                text += REVERSED_MORSE_CODE_DICT[morse_char]
        text += ' '
    return text

# Main function for sender
def sender_main():
    sender_password = getpass.getpass("Sender: Set password for text: ")
    text = input("Sender: Enter text to convert to Morse code: ")
    morse_code = text_to_morse(text)
    
    if not morse_code.strip():
        print("Sender: Invalid text. Please enter valid characters.")
        return
        
    print("Sender: Morse code:", morse_code)
    encryption_key = generate_hashed_password(sender_password)
    encrypted_morse_code = encrypt_morse_code(morse_code, encryption_key)
    
    # Transmit the encrypted Morse code securely to the receiver
    return encrypted_morse_code, sender_password

# Main function for receiver
def receiver_main():
    encrypted_morse_code, sender_password = sender_main()
    receiver_password = getpass.getpass("Receiver: Enter password to decrypt Morse code: ")
    encryption_key = generate_hashed_password(receiver_password)

    # Check if the entered password is valid
    if encryption_key != generate_hashed_password(sender_password):
        print("Receiver: Invalid password. Aborting decryption.")
        return

    decrypted_morse_code = decrypt_morse_code(encrypted_morse_code, encryption_key)
    
    if not decrypted_morse_code.strip():
        print("Receiver: Incorrect Morse code. Aborting decryption.")
        return

    print("Receiver: Decrypted Morse code:", decrypted_morse_code)

    # Convert the decrypted Morse code to text
    text = morse_to_text(decrypted_morse_code)
    print("Receiver: Decoded text:", text.strip())

    # Generate Morse code audio and play
    audio_signal = generate_morse_audio(decrypted_morse_code)
    wav.write("decoded_morse_code.wav", 44100, audio_signal)
    print("Receiver: Morse code audio saved to 'decoded_morse_code.wav' and playing...")
    
    # Uncomment the line below to play the audio (requires a player that supports WAV files)
    #import os;

if __name__ == "__main__":
    receiver_main() # Receiver's code
