import tkinter as tk
from tkinter import scrolledtext
import requests

class USSDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("eNaira USSD")
        self.root.geometry("320x600")
        self.root.configure(bg="#000")

        self.current_text = ""
        self.session_started = False

        # Screen
        self.screen = scrolledtext.ScrolledText(root, height=15, width=30, wrap=tk.WORD, bg="#fff", fg="#000", font=("Arial", 12))
        self.screen.pack(pady=10)
        self.screen.insert(tk.END, "Dial *123# to start")
        self.screen.config(state='disabled')

        # Input field
        self.input_var = tk.StringVar(value="*123#")
        self.input_field = tk.Entry(root, textvariable=self.input_var, width=25, font=("Arial", 12))
        self.input_field.pack()

        # Send button
        self.send_btn = tk.Button(root, text="Send", bg="#28a745", fg="white", command=self.send_request)
        self.send_btn.pack(pady=5)

        # Keypad
        keypad_frame = tk.Frame(root, bg="#000")
        keypad_frame.pack()
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('*', 3, 0), ('0', 3, 1), ('#', 3, 2),
        ]
        for (text, row, col) in buttons:
            bg = "#333" if text in "1234567890" else "#444"
            cmd = lambda x=text: self.append_input(x)
            btn = tk.Button(keypad_frame, text=text, bg=bg, fg="white", width=5, height=2, font=("Arial", 12), command=cmd)
            btn.grid(row=row, column=col, padx=2, pady=2)

        # Bind Enter key
        self.input_field.bind("<Return>", lambda event: self.send_request())

    def append_input(self, char):
        if not self.session_started and char == '*':
            self.current_text = '*123'
        elif self.current_text == '*123' or self.session_started:
            if char == '0' and not self.session_started:
                self.current_text = '*123'
                self.session_started = False
            else:
                if self.current_text and char != '0':
                    self.current_text += '*' + char
                else:
                    self.current_text = char
                self.session_started = True
        self.input_var.set(self.current_text + (char == '#' and '#' or ''))

    def send_request(self):
        text = self.input_var.get()
        if text.endswith('#'):
            text = text[:-1]

        try:
            response = requests.post("http://localhost:5000/ussd", data={
                "sessionId": "12345",
                "phoneNumber": "08012345678",
                "text": text
            })
            response.raise_for_status()
            data = response.json()
            self.screen.config(state='normal')
            self.screen.delete(1.0, tk.END)
            self.screen.insert(tk.END, data['response'])
            self.screen.config(state='disabled')

            if data['response'].startswith('END'):
                self.current_text = ""
                self.session_started = False
                self.input_var.set('*123#')
            else:
                self.current_text = text
                self.input_var.set(text + '*')
        except requests.RequestException as e:
            self.screen.config(state='normal')
            self.screen.delete(1.0, tk.END)
            self.screen.insert(tk.END, f"END Connection error: {str(e)}")
            self.screen.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = USSDApp(root)
    root.mainloop()