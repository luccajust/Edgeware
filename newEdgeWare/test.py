import tkinter as tk
import time


class Window:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("New Window")
        self.window.geometry("200x200")

        label = tk.Label(self.window, text="New Window")
        label.pack(pady=20)


class Main:
    def __init__(self):
        self.windows = []
        self.master = tk.Tk()
        self.master.withdraw()
        self.create_window()

    def create_window(self):
        window = Window(self.master)
        self.windows.append(window)
        self.master.after(10000, self.create_window)  # Schedule to create a new window after 10 seconds

    def start(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = Main()
    app.start()
