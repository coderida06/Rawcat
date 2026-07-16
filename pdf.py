import fitz
import customtkinter as ctk
from tkinter import filedialog
import os
import vlc
import threading
import asyncio
import tempfile
import edge_tts
import json  # Step 1: Import json

# Global VLC Player instance
player = vlc.MediaPlayer()

# Step 2: Create the data folder and library JSON path setup
DATA_FOLDER = "data"
LIBRARY_FILE = os.path.join(DATA_FOLDER, "library.json")
os.makedirs(DATA_FOLDER, exist_ok=True)

if os.path.exists(LIBRARY_FILE):
    try:
        with open(LIBRARY_FILE, "r") as f:
            uploaded_pdfs = json.load(f)
    except:
        uploaded_pdfs = []
else:
    uploaded_pdfs = []

# ---------------- Playback ----------------
# Keep track of active playback states globally or inside reader context
current_mp3_path = None
is_playing = False
playback_speed = 1.0
monitor_after_id = None  # To prevent overlapping tkinter .after loops

# Step 3: Save function near the top
def save_library():
    with open(LIBRARY_FILE, "w") as f:
        json.dump(uploaded_pdfs, f, indent=4)

def clean_temp_file():
    """Safely removes the currently loaded temporary audio file."""
    global current_mp3_path
    if current_mp3_path and os.path.exists(current_mp3_path):
        try:
            player.stop()
            # Force close media to release lock on the file under Windows
            player.set_media(None)
            os.remove(current_mp3_path)
        except Exception as e:
            print(f"Error deleting temp file: {e}")
    current_mp3_path = None

def extract_paragraphs(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()

    # Remove broken line endings
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")

    # Paragraphs in PDFs are usually separated by double spaces after this
    paragraphs = [
        p.strip()
        for p in text.split("  ")
        if len(p.strip()) > 30
    ]

    if not paragraphs:
        paragraphs = [text]

    return paragraphs

def show_pdf_library(app, show_dashboard):
    # Stop playback and clean up audio files when exiting reader
    global is_playing, monitor_after_id
    is_playing = False
    if monitor_after_id:
        app.after_cancel(monitor_after_id)
        monitor_after_id = None
    player.stop()
    clean_temp_file()

    # Step 5: Remove missing files automatically before rendering elements
    global uploaded_pdfs
    uploaded_pdfs[:] = [
        pdf for pdf in uploaded_pdfs
        if os.path.exists(pdf["path"])
    ]
    save_library()

    for widget in app.winfo_children():
        widget.destroy()
        
    back = ctk.CTkButton(
        app,
        text="←",
        width=40,
        fg_color="transparent",
        hover=False,
        font=("Georgia",30),
        command=show_dashboard
    )
    back.place(x=30,y=30)

    title = ctk.CTkLabel(
        app,
        text="PDF Library",
        font=("Underdog",34),
        text_color="white"
    )
    title.place(x=110,y=35)
    
    def upload_pdf():
        filename = filedialog.askopenfilename(
            filetypes=[("PDF Files","*.pdf")]
        )
        if not filename:
            return

        # Step 4: Append new dictionary entry and call save_library()
        uploaded_pdfs.append(
            {
                "name": os.path.basename(filename),
                "path": filename
            }
        )
        save_library()
        show_pdf_library(app, show_dashboard)
        
    upload = ctk.CTkButton(
        app,
        text="Upload PDF",
        width=180,
        height=50,
        fg_color="#27E6C1",
        text_color="black",
        command=upload_pdf
    )
    upload.place(x=480,y=90)
    
    # Step 6: Clear library function and action layout implementation
    def clear_library():
        uploaded_pdfs.clear()
        save_library()
        show_pdf_library(app, show_dashboard)

    clear_button = ctk.CTkButton(
        app,
        text="Clear Library",
        width=180,
        height=50,
        fg_color="#C0392B",
        hover_color="#A93226",
        command=clear_library
    )
    clear_button.place(x=680, y=90)

    # Individual row deletion implementation logic
    def delete_pdf(index):
        uploaded_pdfs.pop(index)
        save_library()
        show_pdf_library(app, show_dashboard)

    for i, pdf in enumerate(uploaded_pdfs):
        card = ctk.CTkButton(
            app,
            text="📕   " + pdf["name"],
            width=520,
            height=60,
            anchor="w",
            command=lambda p=pdf:
                show_pdf_reader(
                    app,
                    show_dashboard,
                    p["path"]
                )
        )
        card.place(
            x=320,
            y=180+i*75
        )

        # Small functional ✕ delete button appended for each item entry card index
        delete = ctk.CTkButton(
            app,
            text="✕",
            width=35,
            height=35,
            fg_color="#C0392B",
            hover_color="#A93226",
            command=lambda i=i: delete_pdf(i)
        )
        delete.place(
            x=860,
            y=192 + i * 75
        )
        
def show_pdf_reader(app, show_dashboard, filepath):
    global playback_speed, is_playing, monitor_after_id
    is_playing = False
    playback_speed = 1.0  # Reset speed on load

    for widget in app.winfo_children():
        widget.destroy()

    paragraphs = extract_paragraphs(filepath)

    if not paragraphs:
        paragraphs = ["No text found in this PDF."]

    current = 0
    is_generating = False  # Lock to prevent multiple thread starts
    
    def display_paragraph():
        counter.configure(
            text=f"Paragraph {current+1} / {len(paragraphs)}"
        )
        paragraph.configure(
            text=paragraphs[current]
        )

    # ---------------- Edge TTS ----------------
    async def generate_tts_async(text, filepath_to_save):
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(filepath_to_save)

    def generate_and_play(paragraph_idx, start_time_ms=0):
        """Generates audio in a background thread and plays it back."""
        nonlocal is_generating
        if is_generating:
            return
        is_generating = True
        
        # Stop existing playback and delete previous file safely
        player.stop()
        clean_temp_file()

        btn_play_pause.configure(text="⌛", state="disabled")

        def run():
            nonlocal is_generating
            try:
                # Setup safe unique temp file
                temp_dir = tempfile.gettempdir()
                new_temp_path = os.path.join(temp_dir, f"rawcat_tts_{paragraph_idx}.mp3")
                
                # Run async TTS generator in sync thread context
                asyncio.run(generate_tts_async(paragraphs[paragraph_idx], new_temp_path))
                
                # Check if user navigated away during generation
                if not is_playing and start_time_ms == 0:
                    is_generating = False
                    # Enable button back but keep visual stopped state
                    app.after(0, lambda: btn_play_pause.configure(text="▶", state="normal"))
                    return

                # ---------------- VLC ----------------
                global current_mp3_path
                current_mp3_path = new_temp_path
                media = vlc.Media(current_mp3_path)
                player.set_media(media)
                player.play()
                
                # Set playback speed and starting seek position
                player.set_rate(playback_speed)
                if start_time_ms > 0:
                    # Small delay to allow VLC initialization before seeking
                    import time
                    time.sleep(0.15)
                    player.set_time(int(start_time_ms))

                # Update UI elements
                app.after(0, lambda: btn_play_pause.configure(text="⏸", state="normal"))
                
            except Exception as e:
                print(f"Error during TTS generation/playback: {e}")
                app.after(0, lambda: btn_play_pause.configure(text="▶", state="normal"))
            finally:
                is_generating = False

        threading.Thread(target=run, daemon=True).start()

    # ---------------- Playback ----------------
    def toggle_play_pause():
        global is_playing
        if is_generating:
            return

        if is_playing:
            # Pause playback
            player.pause()
            is_playing = False
            btn_play_pause.configure(text="▶")
        else:
            # Resume or Start Fresh
            is_playing = True
            state = player.get_state()
            if state == vlc.State.Paused:
                player.play()
                player.set_rate(playback_speed)
                btn_play_pause.configure(text="⏸")
            else:
                generate_and_play(current)

    def change_speed(value):
        global playback_speed
        # Convert string "1.5x" -> float 1.5
        playback_speed = float(value.replace("x", ""))
        player.set_rate(playback_speed)

    def seek_backward():
        nonlocal current
        if is_generating:
            return
        
        current_time = player.get_time()  # in ms
        target_time = current_time - 10000

        if target_time >= 0:
            player.set_time(int(target_time))
        else:
            # Seek backwards into the previous paragraph
            if current > 0:
                current -= 1
                display_paragraph()
                # Find length of previous paragraph audio dynamically
                # To seek properly, we generate and start at the end minus the remainder
                underflow = abs(target_time)
                
                # Generate previous and calculate start position
                temp_dir = tempfile.gettempdir()
                test_path = os.path.join(temp_dir, f"rawcat_tts_temp_len.mp3")
                
                def run_back_seek():
                    try:
                        asyncio.run(generate_tts_async(paragraphs[current], test_path))
                        # Get temporary duration details
                        m = vlc.Media(test_path)
                        p = vlc.MediaPlayer()
                        p.set_media(m)
                        p.play()
                        import time
                        time.sleep(0.1)  # Allow duration initialization
                        duration = p.get_length()
                        p.stop()
                        os.remove(test_path)
                        
                        start_pos = max(0, duration - underflow)
                        app.after(0, lambda: generate_and_play(current, start_pos))
                    except Exception as e:
                        print(e)
                        app.after(0, lambda: generate_and_play(current))
                        
                threading.Thread(target=run_back_seek, daemon=True).start()
            else:
                player.set_time(0)

    def seek_forward():
        nonlocal current
        if is_generating:
            return

        current_time = player.get_time()  # in ms
        duration = player.get_length()     # in ms
        target_time = current_time + 10000

        if duration > 0 and target_time < duration:
            player.set_time(int(target_time))
        else:
            # Seek forward into the next paragraph
            if current < len(paragraphs) - 1:
                overflow = target_time - (duration if duration > 0 else current_time)
                current += 1
                display_paragraph()
                generate_and_play(current, start_time_ms=overflow)
            else:
                # Stop if end of PDF reached
                player.stop()
                global is_playing
                is_playing = False
                btn_play_pause.configure(text="▶")

    def monitor_playback():
        """Automatically runs every 100ms on the main GUI thread to coordinate auto-advance."""
        global is_playing, monitor_after_id
        if is_playing and not is_generating:
            state = player.get_state()
            # If the current paragraph has naturally ended, advance to the next
            if state == vlc.State.Ended:
                nonlocal current
                if current < len(paragraphs) - 1:
                    current += 1
                    display_paragraph()
                    generate_and_play(current)
                else:
                    is_playing = False
                    btn_play_pause.configure(text="▶")
                    player.stop()
                    clean_temp_file()
                    
        # Loop monitor
        monitor_after_id = app.after(100, monitor_playback)

    # Clean up any existing playback callbacks/sessions before starting anew
    if monitor_after_id:
        app.after_cancel(monitor_after_id)
        monitor_after_id = None
        
    back = ctk.CTkButton(
        app,
        text="←",
        width=40,
        fg_color="transparent",
        hover=False,
        font=("Georgia",30),
        command=lambda: show_pdf_library(app, show_dashboard)
    )
    back.place(x=30,y=30)
    
    file = ctk.CTkLabel(
        app,
        text=os.path.basename(filepath),
        font=("Underdog",28),
        text_color="white"
    )
    file.place(x=110,y=35)

    # Counter label
    counter = ctk.CTkLabel(
        app,
        text="",
        font=("Segoe UI",16),
        text_color="#A0A0A0"
    )
    counter.place(x=210,y=110)
    
    frame = ctk.CTkFrame(
        app,
        width=760,
        height=340,
        corner_radius=20
    )
    frame.place(x=200,y=140)
    
    paragraph = ctk.CTkLabel(
        frame,
        text="",
        wraplength=700,
        justify="left",
        font=("Segoe UI",20)
    )
    paragraph.place(
        x=20,
        y=20
    )

    # ---------------- UI Widgets ----------------
    speed_var = ctk.StringVar(value="1.0x")
    dropdown_speed = ctk.CTkOptionMenu(
        app,
        values=["0.75x", "1.0x", "1.25x", "1.5x", "2.0x"],
        command=change_speed,
        variable=speed_var,
        width=90,
        height=40
    )
    dropdown_speed.place(x=200, y=500)

    btn_seek_back = ctk.CTkButton(
        app,
        text="⏪10",
        font=("Segoe UI", 16),
        width=100,
        height=40,
        command=seek_backward
    )
    btn_seek_back.place(x=380, y=500)

    btn_play_pause = ctk.CTkButton(
        app,
        text="▶",
        font=("Segoe UI", 20),
        fg_color="#27E6C1",
        text_color="black",
        width=140,
        height=40,
        command=toggle_play_pause
    )
    btn_play_pause.place(x=510, y=500)

    btn_seek_forward = ctk.CTkButton(
        app,
        text="10⏩",
        font=("Segoe UI", 16),
        width=100,
        height=40,
        command=seek_forward
    )
    btn_seek_forward.place(x=680, y=500)
    
    display_paragraph()
    monitor_playback()
