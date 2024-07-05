import tkinter as tk
from tkinter import scrolledtext, Frame, Button
from firebase_admin import credentials, initialize_app, db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.dates as mdates
import threading

# Initialize Firebase admin SDK
databaseURL = 'https://task1-a7033-default-rtdb.firebaseio.com/'
cred_obj = credentials.Certificate('task1-a7033-firebase-adminsdk-cmgki-bf83ccca15.json')
default_app = initialize_app(cred_obj, {'databaseURL': databaseURL})

# Set up the Tkinter application
class DataMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Firebase Data Monitor")
        self.root.configure(bg="#f0f0f0")  # Set background color

        # Create a frame for the text display
        self.text_frame = Frame(root, bg="#f0f0f0")
        self.text_frame.pack(side="right", fill="both", expand=True)
        
        self.display = scrolledtext.ScrolledText(self.text_frame, width=70, height=10, bg="#f0f0f0", fg="black", font=("Arial", 12))
        self.display.pack(pady=20)

        # Create a frame for the charts
        self.chart_frame = Frame(root, bg="#f0f0f0")
        self.chart_frame.pack(side="left", fill="both", expand=True)

        # Setting up the ultrasonic chart
        self.fig1, self.ax1 = plt.subplots(figsize=(5, 4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.chart_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.ultrasonic_dates = []
        self.ultrasonic_values = []

        # Setting up the flame chart
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.chart_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.flame_dates = []
        self.flame_values = []

        # Initialize the Firebase listener in a new thread
        self.firebase_thread = threading.Thread(target=self.start_firebase_listener)
        self.firebase_thread.daemon = True
        self.firebase_thread.start()

        # Add a button to clear the display
        self.clear_button = Button(self.text_frame, text="Clear Display", command=self.clear_display, bg="#007acc", fg="white")
        self.clear_button.pack(pady=10)

    def start_firebase_listener(self):
        ref = db.reference("/readings")
        ref.listen(self.firebase_listener)

    def firebase_listener(self, event):
        try:
            # Check for dict structure and key existence
            if isinstance(event.data, dict) and 'ultrasonic_value' in event.data and 'flame_value' in event.data:
                ultrasonic_value = event.data['ultrasonic_value']
                flame_value = event.data['flame_value']
                timestamp = datetime.fromtimestamp(event.data['timestamp'] / 1000)
                
                # Schedule GUI update in the main thread
                self.root.after(0, lambda: self.update_ultrasonic_chart(timestamp, ultrasonic_value))
                self.root.after(0, lambda: self.update_flame_chart(timestamp, flame_value))
                
                event_data = f"Ultrasonic Value: {ultrasonic_value}, Flame Value: {flame_value}\n"
                self.update_display(event_data)
                
                # Change background color based on flame detection
                if flame_value == 1:
                    self.root.configure(bg="#ffcccc")  # Light red
                else:
                    self.root.configure(bg="#f0f0f0")  # Light gray
                
        except Exception as e:
            print(f"Error processing event data: {e}")

    def update_display(self, message):
        # Update the display with new Firebase event data, keeping only last 10 entries
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, message)
        self.display_contents = self.display.get('1.0', tk.END).split('\n\n')
        if len(self.display_contents) > 10:  # Keep only the last 10 records
            self.display.delete('1.0', tk.END)
            new_content = '\n\n'.join(self.display_contents[-11:])
            self.display.insert(tk.END, new_content)
        self.display.config(state=tk.DISABLED)
        self.display.see(tk.END)

    def clear_display(self):
        # Clear the display
        self.display.config(state=tk.NORMAL)
        self.display.delete('1.0', tk.END)
        self.display.config(state=tk.DISABLED)

    def update_ultrasonic_chart(self, timestamp, ultrasonic_value):
        # Add new data to the ultrasonic chart and redraw, keeping only last 10 entries
        self.ultrasonic_dates.append(timestamp)
        self.ultrasonic_values.append(ultrasonic_value)
        if len(self.ultrasonic_dates) > 10:  # Limit the lists to last 10 entries
            self.ultrasonic_dates = self.ultrasonic_dates[-10:]
            self.ultrasonic_values = self.ultrasonic_values[-10:]
        
        self.ax1.clear()
        self.ax1.plot(self.ultrasonic_dates, self.ultrasonic_values, marker='o', color='#007acc')  # Blue
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax1.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Ultrasonic Value")
        self.fig1.autofmt_xdate()
        self.canvas1.draw()

    def update_flame_chart(self, timestamp, flame_value):
        # Add new data to the flame chart and redraw, keeping only last 10 entries
        self.flame_dates.append(timestamp)
        self.flame_values.append(flame_value)
        if len(self.flame_dates) > 10:  # Limit the lists to last 10 entries
            self.flame_dates = self.flame_dates[-10:]
            self.flame_values = self.flame_values[-10:]
        
        self.ax2.clear()
        # Convert flame value to binary for better visualization
        binary_flame_values = [1 if value == 1 else 0 for value in self.flame_values]
        self.ax2.plot(self.flame_dates, binary_flame_values, marker='o', color='#ff7f0e')  # Orange
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax2.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Flame Detection (1: Yes, 0: No)")
        self.fig2.autofmt_xdate()
        self.canvas2.draw()

# Create the main window and pass it to the DataMonitorApp class
if __name__ == "__main__":
    root = tk.Tk()
    app = DataMonitorApp(root)
    root.mainloop()
