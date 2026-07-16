import customtkinter as ctk
import calendar
import json
import os
from datetime import datetime

# ==========================================
# PERSISTENCE SETUP & INITIALIZATION
# ==========================================
DATA_FOLDER = "data"
TODO_FILE = os.path.join(DATA_FOLDER, "todo.json")
LIBRARY_FILE = os.path.join(DATA_FOLDER, "library.json")

os.makedirs(DATA_FOLDER, exist_ok=True)

# Load To-Do Data
if os.path.exists(TODO_FILE):
    try:
        with open(TODO_FILE, "r") as f:
            todo_data = json.load(f)
    except:
        todo_data = {}
else:
    todo_data = {}

# Load PDF Library Data
if os.path.exists(LIBRARY_FILE):
    try:
        with open(LIBRARY_FILE, "r") as f:
            uploaded_pdfs = json.load(f)
    except:
        uploaded_pdfs = []
else:
    uploaded_pdfs = []

if 'selected_date_str' not in globals():
    selected_date_str = datetime.now().strftime("%Y-%m-%d")


# ==========================================
# SAVE FUNCTIONS
# ==========================================
def save_todo():
    with open(TODO_FILE, "w") as f:
        json.dump(todo_data, f, indent=4)

def save_library():
    with open(LIBRARY_FILE, "w") as f:
        json.dump(uploaded_pdfs, f, indent=4)


# ==========================================
# GUI APPLICATION CODE
# ==========================================
def show_todo(app, show_dashboard, year=None, month=None):
    global selected_date_str

    # Current month if none supplied
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Clear window
    for widget in app.winfo_children():
        widget.destroy()

    # =========================
    # BACK BUTTON
    # =========================
    back = ctk.CTkButton(
        app,
        text="←",
        width=40,
        fg_color="transparent",
        hover=False,
        font=("Georgia", 30),
        command=show_dashboard
    )
    back.place(x=25, y=25)

    # =========================
    # MONTH
    # =========================
    month_name = datetime(year, month, 1).strftime("%B %Y")

    month_label = ctk.CTkLabel(
        app,
        text=month_name,
        font=("Underdog", 32),
        text_color="white"
    )
    month_label.place(x=145, y=40)

    # =========================
    # MONTH BUTTONS
    # =========================
    def previous_month():
        new_month = month - 1
        new_year = year

        if new_month == 0:
            new_month = 12
            new_year -= 1

        show_todo(app, show_dashboard, new_year, new_month)

    def next_month():
        new_month = month + 1
        new_year = year

        if new_month == 13:
            new_month = 1
            new_year += 1

        show_todo(app, show_dashboard, new_year, new_month)

    prev_button = ctk.CTkButton(
        app,
        text="◀",
        width=30,
        fg_color="transparent",
        hover=False,
        font=("Segoe UI", 22),
        command=previous_month
    )
    prev_button.place(x=90, y=42)

    next_button = ctk.CTkButton(
        app,
        text="▶",
        width=30,
        fg_color="transparent",
        hover=False,
        font=("Segoe UI", 22),
        command=next_month
    )
    next_button.place(x=360, y=42)

    # =========================
    # WEEKDAYS
    # =========================
    weekdays = ["S", "M", "T", "W", "T", "F", "S"]

    for i, day in enumerate(weekdays):
        lbl = ctk.CTkLabel(
            app,
            text=day,
            font=("Segoe UI", 18),
            text_color="#8F96C5"
        )
        lbl.place(x=55 + i * 55, y=115)

    # =========================
    # CALENDAR
    # =========================
    month_days = calendar.monthcalendar(year, month)

    for row, week in enumerate(month_days):
        for col, day in enumerate(week):
            if day == 0:
                continue

            # Compare to highlight selected day in mint green
            day_str = f"{year}-{month:02d}-{day:02d}"
            if day_str == selected_date_str:
                bg_color = "#27E6C1"  # Mint Green
                txt_color = "black"
            else:
                bg_color = "#1A214A"
                txt_color = "white"

            # Capture current loop state using a default parameter value
            def make_date_click_handler(d=day):
                return lambda: select_date(d)

            button = ctk.CTkButton(
                app,
                text=str(day),
                width=42,
                height=42,
                corner_radius=10,
                fg_color=bg_color,
                text_color=txt_color,
                hover_color="#38D6B5",
                font=("Segoe UI", 16),
                command=make_date_click_handler(day)
            )

            button.place(
                x=40 + col * 55,
                y=150 + row * 52
            )

    # =========================
    # RIGHT PANEL
    # =========================
    # Convert currently stored date string into readable text format
    current_dt = datetime.strptime(selected_date_str, "%Y-%m-%d")
    readable_date = current_dt.strftime("%d %B %Y")

    selected = ctk.CTkLabel(
        app,
        text=readable_date,
        font=("Underdog", 28),
        text_color="white"
    )
    selected.place(x=470, y=55)

    # List tracking actively displayed checkboxes to destroy during redraws
    active_checkboxes = []

    def refresh_tasks():
        # Clear any existing checkboxes currently on the screen
        for cb in active_checkboxes:
            cb.destroy()
        active_checkboxes.clear()

        # Fetch current date's tasks list
        day_tasks = todo_data.get(selected_date_str, [])

        # Render tasks dynamically
        for idx, task_info in enumerate(day_tasks):
            
            # State capturer function for checkbox trigger states
            def make_check_handler(t_info=task_info):
                return lambda: toggle_task(t_info)

            # Move to a new column on the side after every 4 tasks
            col_idx = idx // 4
            row_idx = idx % 4

            task_check = ctk.CTkCheckBox(
                app,
                text=task_info["text"],
                width=200,  # Adjusted width to accommodate side-by-side columns
                font=("Segoe UI", 21),
                text_color="white",
                command=make_check_handler(task_info)
            )
            
            # Places new columns spaced out cleanly to the right
            task_check.place(
                x=470 + (col_idx * 215),
                y=120 + row_idx * 45
            )
            
            if task_info["done"]:
                task_check.select()
            else:
                task_check.deselect()

            active_checkboxes.append(task_check)

    def select_date(day_num):
        global selected_date_str
        selected_date_str = f"{year}-{month:02d}-{day_num:02d}"
        
        # Redraw layout to refresh active calendar highlights and loaded lists
        show_todo(app, show_dashboard, year, month)

    def toggle_task(task_info):
        task_info["done"] = not task_info["done"]
        save_todo()  # Save data after shifting completion state
        refresh_tasks()

    def add_new_task():
        task_text = task_entry.get().strip()
        if not task_text:
            return 

        if selected_date_str not in todo_data:
            todo_data[selected_date_str] = []

        todo_data[selected_date_str].append({"text": task_text, "done": False})
        save_todo()  # Save data after appending a new entry
        
        task_entry.delete(0, 'end')
        refresh_tasks()

    def clear_day():
        if selected_date_str in todo_data:
            del todo_data[selected_date_str]
            save_todo()
            refresh_tasks()

    # =========================
    # ACTION CONTROLS (ADD / CLEAR)
    # =========================
    task_entry = ctk.CTkEntry(
        app,
        width=320,
        height=42,
        placeholder_text="Add a task..."
    )
    task_entry.place(x=470, y=370)

    add_button = ctk.CTkButton(
        app,
        text="Add",
        width=90,
        height=42,
        fg_color="#27E6C1",
        text_color="black",
        command=add_new_task
    )
    add_button.place(x=810, y=370)

    clear_button = ctk.CTkButton(
        app,
        text="Clear Day",
        width=100,
        height=42,
        fg_color="#FF5A5A",
        hover_color="#E04343",
        text_color="white",
        command=clear_day
    )
    clear_button.place(x=915, y=370)

    # Initial paint cycle run
    refresh_tasks()
