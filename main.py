import customtkinter as ctk
from datetime import datetime
import winsound
from PIL import Image
from todo import show_todo
from pdf import show_pdf_library

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("1160x580")
app.configure(fg_color="#101b33")
app.title("rawcat")

logo = ctk.CTkImage(
    light_image=Image.open("assets/rawcatlogo.png"),
    dark_image=Image.open("assets/rawcatlogo.png"),
    size=(270, 320)
)

logo_label = ctk.CTkLabel(
    app,
    image=logo,
    text=""
)

logo_label.place(x=260, y=20)

bookshelf = ctk.CTkImage(
    light_image=Image.open("assets/bookshelf.jpg"),
    dark_image=Image.open("assets/bookshelf.jpg"),
    size=(180, 180)
)

for i in range(7):
    shelf = ctk.CTkLabel(
        app,
        image=bookshelf,
        text=""
    )
    shelf.place(x=0, y=i * 80)
    
for i in range(15):
    shelf = ctk.CTkLabel(
        app,
        image=bookshelf,
        text=""
    )
    shelf.place(x=i * 80, y=500)
    
title = ctk.CTkLabel(
    app,
    text="rawcat",
    font=("Underdog", 67),
    text_color="white"
)

title.place(x=490, y=130)

sometext = ctk.CTkLabel(
    app,
    text='"Ive studied too much" -said no smart person ever.',
    font=("Underdog", 24),
    text_color="white"
)

sometext.place(x=400, y=400)

somemoretext = ctk.CTkLabel(
    app,
    text='Lock In twin.',
    font=("Underdog", 24),
    text_color="white"
)

somemoretext.place(x=895, y=290)



def start_timer(focus, break_time, sessions):

    for widget in app.winfo_children():
        widget.destroy()

    total_seconds = focus * 60
    seconds_left = total_seconds
    is_focus = True
    current_session = 1
    paused = False
    
        # Back button
    back1 = ctk.CTkButton(
    app,
    text="←",
    font=("Georgia", 38),
    width=40,
    fg_color="transparent",
    hover=False,
    command=show_dashboard
)

    back1.place(x=40, y=40)

    def pause_timer():
        nonlocal paused

        paused = not paused

        if paused:
            pause_button.configure(text="▶")

        else:
            pause_button.configure(text="⏸")
            update_timer()

    def restart_timer():
        nonlocal seconds_left
        nonlocal total_seconds
        nonlocal is_focus

        if is_focus:
            total_seconds = focus * 60
            seconds_left = total_seconds
        else:
            total_seconds = break_time * 60
            seconds_left = total_seconds

        progress.set(1)
        update_timer()

     

    def update_timer():
        nonlocal seconds_left
        nonlocal total_seconds
        nonlocal is_focus
        nonlocal current_session
        nonlocal paused
        
        if paused:
            return

        minutes = seconds_left // 60
        seconds = seconds_left % 60

        timer_label.configure(
            text=f"{minutes:02}:{seconds:02}"
        )

        progress.set(seconds_left / total_seconds)

        if seconds_left > 0:
            seconds_left -= 1
            app.after(1000, update_timer)

        else:

            if is_focus:

                # Focus finished
                for i in range(5):
                    winsound.Beep(1000, 200)
                    winsound.Beep(1200, 200)

    # If that was the last focus session, we're done
                if current_session == sessions:
                    timer_title.configure(text="DONE!")
                    timer_label.configure(text="00:00")
                    progress.set(0)
                    return

    # Otherwise start the break
                is_focus = False

                timer_title.configure(text="BREAK")

                total_seconds = break_time * 60
                seconds_left = total_seconds

                update_timer()

            else:

                # Break finished
                for i in range(15):
                    winsound.Beep(700, 500)

                current_session += 1


                is_focus = True

                timer_title.configure(text="FOCUS")

                total_seconds = focus * 60
                seconds_left = total_seconds

                update_timer()

    
    timer_title = ctk.CTkLabel(
    app,
    text="FOCUS",
    font=("Underdog", 28),
    text_color="white"
)
    timer_title.place(x=630, y=70)
    
    timer_label = ctk.CTkLabel(
    app,
    text=f"{focus:02}:00",
    font=("Underdog", 72),
    text_color="white"
)
    timer_label.place(x=580, y=300)
    
    pause_button = ctk.CTkButton(
    app,
    text="⏸",
    width=60,
    fg_color="transparent",
    hover=False,
    font=("Segoe UI",28),
    command=pause_timer
)
    
    pause_button.place(x=370, y=300)
    
    restart_button = ctk.CTkButton(
    app,
    text="Restart",
    fg_color="transparent",
    hover=False,
    text_color="#27E6C1",
    command=restart_timer
)
    restart_button.place(x=800, y=300)

    progress = ctk.CTkProgressBar(
    app,
    width=300,
    height=12,
    progress_color="white",
    fg_color="black"
)

    progress.place(x=480, y=500)
    progress.set(1)
    update_timer()

#pomodoro page
def show_pomodoro():

    # Remove dashboard widgets
    for widget in app.winfo_children():
        widget.destroy()

    # Back button
    back = ctk.CTkButton(
    app,
    text="←",
    font=("Georgia", 38),
    width=40,
    fg_color="transparent",
    hover=False,
    command=show_dashboard
)

    back.place(x=40, y=40)
    
    focus_label = ctk.CTkLabel(
    app,
    text="Focus period:",
    font=("Georgia", 25),
    text_color="white"
)

    focus_label.place(x=250, y=160)
    
    focus_hours_entry = ctk.CTkEntry(
    app,
    width=100,
    height=40,
    font=("Segoe UI", 18),
    placeholder_text="H"
)
    focus_hours_entry.place(x=600, y=160)

    focus_mins_entry = ctk.CTkEntry(
    app,
    width=100,
    height=40,
    font=("Segoe UI", 18),
    placeholder_text="M"
)
    focus_mins_entry.place(x=720, y=160)
    
    break_label = ctk.CTkLabel(
    app,
    text="Break duration:",
    font=("Georgia", 25),
    text_color="white"
)

    break_label.place(x=250, y=290)
    
    break_hours_entry = ctk.CTkEntry(
    app,
    width=100,
    height=40,
    font=("Segoe UI", 18),
    placeholder_text="H"
)
    break_hours_entry.place(x=600, y=290)

    break_mins_entry = ctk.CTkEntry(
    app,
    width=100,
    height=40,
    font=("Segoe UI", 18),
    placeholder_text="M"
)
    break_mins_entry.place(x=720, y=290)
    
    sessions_label = ctk.CTkLabel(
    app,
    text="Number of sessions:",
    font=("Georgia", 25),
    text_color="white"
)

    sessions_label.place(x=220, y=420)
    
    sessions_entry = ctk.CTkEntry(
    app,
    width=220,
    height=40,
    font=("Segoe UI", 18)
)

    sessions_entry.place(x=600, y=420)
    
    # helper conversion wrapper to handle empty entries safely
    def get_int_value(entry):
        val = entry.get().strip()
        return int(val) if val.isdigit() else 0

    # lockin button
    lockin_button = ctk.CTkButton(
    app,
    text="Lock In",
    width=200,
    height=70,
    font=("underdog", 29),
    fg_color="#7486ba",
    hover_color="#101b33",
    text_color="black",
    command=lambda: start_timer(
        (get_int_value(focus_hours_entry) * 60) + get_int_value(focus_mins_entry),
        (get_int_value(break_hours_entry) * 60) + get_int_value(break_mins_entry),
        get_int_value(sessions_entry)
    )
)

    lockin_button.place(x=570, y=500)
    
    
    quote = ctk.CTkLabel(
    app,
    text='POMODORO TIMER',
    font=("Underdog", 24),
    text_color="white"
)

    quote.place(x=490, y=70)


def show_dashboard():

    # Clear home page
    for widget in app.winfo_children():
        widget.destroy()

    # Dashboard title
    dashboard = ctk.CTkLabel(
        app,
        text="Dashboard",
        font=("Underdog", 30),
        text_color="white"
    )
    dashboard.pack()
    
    # Logo image
    logo = ctk.CTkImage(
    light_image=Image.open("assets/rawcatlogo.png"),
    dark_image=Image.open("assets/rawcatlogo.png"),
    size=(120, 140)
)

    logo_label = ctk.CTkLabel(
    app,
    image=logo,
    text=""
)

    logo_label.place(x=20, y=7)
    
    title = ctk.CTkLabel(
    app,
    text="rawcat",
    font=("Underdog", 48),
    text_color="white"
)

    title.place(x=110, y=40)

    # Create the clock
    clock_label = ctk.CTkLabel(
        app,
        text="",
        font=("Underdog", 30),
        text_color="white"
    )
    clock_label.place(x=1030, y=30)

    # Update function
    def update_clock():
        current_time = datetime.now().strftime("%I:%M %p")
        clock_label.configure(text=current_time)
        app.after(1000, update_clock)

    update_clock()
    

    # todo Image


    todo = ctk.CTkImage(
    light_image=Image.open("assets/todo.png"),
    dark_image=Image.open("assets/todo.png"),
    size=(200, 240)      # Change to your image size
)

    todo_button = ctk.CTkButton(
    app,
    image=todo,
    text="",
    width=180,
    height=220,
    fg_color="transparent",
    hover_color="#09ce9a",      
    border_width=0,
    corner_radius=0,
    command=lambda: show_todo(app, show_dashboard)
)

    todo_button.place(x=130, y=210)
    
        # pdf Image


    pdf = ctk.CTkImage(
    light_image=Image.open("assets/pdf.png"),
    dark_image=Image.open("assets/pdf.png"),
    size=(200, 240)      
)

    pdf_button = ctk.CTkButton(
    app,
    image=pdf,
    text="",
    width=180,
    height=220,
    fg_color="transparent",
    hover_color="#1034a0",      
    border_width=0,
    corner_radius=0,
    command=lambda: show_pdf_library(app, show_dashboard)
)

    pdf_button.place(x=510, y=210)
    
    #pomodoro button
    
    pomodoro = ctk.CTkImage(
    light_image=Image.open("assets/pomodoro.png"),
    dark_image=Image.open("assets/pomodoro.png"),
    size=(200, 240)      
)

    pomodoro_button = ctk.CTkButton(
    app,
    image=pomodoro,
    text="",
    width=180,
    height=220,
    fg_color="transparent",
    hover_color="#7486ba",      
    border_width=0,
    corner_radius=0,
    command=show_pomodoro
)

    pomodoro_button.place(x=890, y=210)
    

play_button = ctk.CTkButton(
    app,
    text="Play",
    width=200,
    height=70,
    font=("indigo", 29),
    fg_color="#27E6C1",
    hover_color="#1BC6A5",
    text_color="black",
    command=show_dashboard
)

play_button.place(x=860, y=200)

app.mainloop()
