import tkinter as tk
import calendar
from tkinter import ttk
from datetime import datetime


def create_calendar(root, year, month):
    cal = calendar.month(year, month)
    tk.Label(root, text=cal).pack()


def main():
    root = tk.Tk()
    now = datetime.now()
    create_calendar(root, now.year, now.month)
    root.title("日历")
    root.mainloop()


if __name__ == "__main__":
    main()