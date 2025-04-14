import requests
import time

class USSDClient:
    def __init__(self, base_url="http://localhost:5000/ussd"):
        self.base_url = base_url
        self.session_id = "12345"  # Fixed session ID for simplicity
        self.phone_number = "08012345678"  # Default user (user1)
        self.text = ""  # Tracks the USSD input string

    def send_request(self, user_input=None):
        if user_input is not None:
            if self.text and user_input != "0":  # Append input with '*' unless resetting
                self.text += f"*{user_input}"
            else:
                self.text = user_input if user_input != "0" else ""

        data = {
            "sessionId": self.session_id,
            "phoneNumber": self.phone_number,
            "text": self.text
        }
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
            return response.json().get("response", "END Server error")
        except requests.RequestException as e:
            return f"END Connection error: {str(e)}"

    def run(self):
        print("Welcome to eNaira Offline USSD System")
        print("Dial *123# to start (or type 'exit' to quit)")
        
        while True:
            user_input = input("> ").strip()

            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            elif user_input == "*123#":
                self.text = ""  # Reset session
                response = self.send_request()
                print(response)
            elif self.text or user_input in ["0", "1", "2", "3", "4"]:
                response = self.send_request(user_input)
                print(response)
                # If the response starts with "END", reset the session
                if response.startswith("END"):
                    self.text = ""
            else:
                print("Invalid input. Dial *123# to start.")

if __name__ == "__main__":
    # Ensure the Flask server (app.py) is running before starting the client
    client = USSDClient()
    client.run()