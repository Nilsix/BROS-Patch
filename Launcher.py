import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

path = filedialog.askdirectory()
print(path)
a = input("pause")
