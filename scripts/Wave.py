#----------------------------------------------------------------------------------#
# By Emanuel Nunez and Edward White
# Edited by Harry Williams for open hand detection
# Version 2
#----------------------------------------------------------------------------------#

# Importing required libraries
import cv2
import mediapipe as mp
import socket
from threading import Thread, Lock
import time

# Define the server (computer) details
host = '0.0.0.0'    # Localhost
port = 8888         # Port number

# Define the SimpleServer class
class SimpleServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.lock = Lock()

        self.start_server()

    def start_server(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the address and port
        self.server_socket.bind((self.host, self.port))
        # Listen for incoming connections
        self.server_socket.listen(1)

        # Start a thread to accept client connections
        accept_thread = Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        while True:
            self.client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address} has been established.")

    def send_signal(self, message):
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.sendall(message.encode())
                    print(f"Sent message: {message}")
                except (BrokenPipeError, ConnectionResetError):
                    self.client_socket = None
                    print("Client disconnected.")
            else:
                print("No client connected.")

# Main function
def detectWave():
    # At very start, open webcam
    video_capture = cv2.VideoCapture(0) # sometimes called "cap"

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils
    debounce_rude = 0
    debounce_wave = 0

    while video_capture.isOpened():
        time.sleep(0.2)
        # Step 1: Read frame from camera
        success, image = video_capture.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Step 2: Image processing
        image = image_processing(image)

        # Step 3: Hand detection
        mediapipe_results = hands.process(image)

        if mediapipe_results.multi_hand_landmarks:
                for hand_landmarks in mediapipe_results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Detecting hand raise (basic example, you might need to fine-tune this)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    middle_tip =  hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    middle_DIP = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
                    middle_palm = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    ring_tip =  hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    

                    if middle_tip.y < middle_palm.y and middle_palm.y < wrist.y:
                        if index_tip.y > middle_DIP.y and ring_tip.y > middle_DIP.y and pinky_tip.y > middle_DIP.y:
                            debounce_rude += 1
                            debounce_wave = 0
                            if debounce_rude == 5:
                                debounce_rude = 0
                                print("Rude")
                                signal_thread = Thread(target=server.send_signal, args=("Rude",))
                                signal_thread.start()
                        else:
                            debounce_wave += 1
                            debounce_rude = 0
                            if debounce_wave == 5:
                                debounce_wave = 0
                                print("Wave")
                                signal_thread = Thread(target=server.send_signal, args=("Wave",))
                                signal_thread.start()
                    


        # Step 4: Display output
        cv2.imshow('Hand Detection', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(5) & 0xFF == 27:
            break

    # At end, close it
    video_capture.release()


def image_processing(image):
    # Step 2.1: Convert the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    return image


if __name__ == "__main__":
     # First, create the server socket in a separate thread
    print("Creating server...")
    server = SimpleServer(host, port)
    print("Server created.")
    while server.client_socket is None:
        time.sleep(1)  # Wait for the client to connect
    while True:
        detectWave()
