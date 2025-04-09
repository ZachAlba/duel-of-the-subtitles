import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os

def browse_file(entry):
    path = filedialog.askopenfilename()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def browse_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def run_subtitle_script():
    video = video_entry.get()
    sub = sub_entry.get()
    output = output_entry.get()
    debug = "--debug" if debug_var.get() else ""
    offset = offset_entry.get()

    command = ["python", "subtitle_script.py", video, sub, output]
    if debug:
        command.append(debug)
    if offset:
        command.extend(["--offset", offset])
    
    log_text.delete("1.0", tk.END)
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        log_text.insert(tk.END, result.stdout + "\n" + result.stderr)
    except Exception as e:
        log_text.insert(tk.END, str(e))

def run_vtt_shift():
    input_file = shift_input_entry.get()
    output_file = shift_output_entry.get()
    shift = shift_seconds_entry.get()

    command = ["python", "vtt_adjuster.py", "shift", input_file, output_file, shift]
    log_text.delete("1.0", tk.END)
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        log_text.insert(tk.END, result.stdout + "\n" + result.stderr)
    except Exception as e:
        log_text.insert(tk.END, str(e))

def run_vtt_combine():
    vtt1 = combine_vtt1_entry.get()
    vtt2 = combine_vtt2_entry.get()
    output = combine_output_entry.get()
    duration = ep1_duration_entry.get()

    command = ["python", "vtt_adjuster.py", "combine", vtt1, vtt2, output, duration]
    log_text.delete("1.0", tk.END)
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        log_text.insert(tk.END, result.stdout + "\n" + result.stderr)
    except Exception as e:
        log_text.insert(tk.END, str(e))

root = tk.Tk()
root.title("Subtitle Processing GUI")

tab_control = ttk.Notebook(root)

# --- Subtitle Script Tab ---
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Video + Subtitles")

tk.Label(tab1, text="Video Path (file or folder)").grid(row=0, column=0, sticky='w')
video_entry = tk.Entry(tab1, width=50)
video_entry.grid(row=0, column=1)
tk.Button(tab1, text="Browse", command=lambda: browse_file(video_entry)).grid(row=0, column=2)

tk.Label(tab1, text="Subtitle Path (file or folder)").grid(row=1, column=0, sticky='w')
sub_entry = tk.Entry(tab1, width=50)
sub_entry.grid(row=1, column=1)
tk.Button(tab1, text="Browse", command=lambda: browse_file(sub_entry)).grid(row=1, column=2)

tk.Label(tab1, text="Output Path (file or folder)").grid(row=2, column=0, sticky='w')
output_entry = tk.Entry(tab1, width=50)
output_entry.grid(row=2, column=1)
tk.Button(tab1, text="Browse", command=lambda: browse_folder(output_entry)).grid(row=2, column=2)

debug_var = tk.BooleanVar()
tk.Checkbutton(tab1, text="Debug Mode (1 min)", variable=debug_var).grid(row=3, column=1, sticky='w')

tk.Label(tab1, text="Subtitle Offset (seconds)").grid(row=4, column=0, sticky='w')
offset_entry = tk.Entry(tab1)
offset_entry.grid(row=4, column=1)

tk.Button(tab1, text="Run Subtitle Script", command=run_subtitle_script).grid(row=5, column=1)

# --- VTT Adjuster Tab ---
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="VTT Adjuster")

# Shift
tk.Label(tab2, text="Shift Subtitle Timings").grid(row=0, column=1)
tk.Label(tab2, text="Input VTT").grid(row=1, column=0)
shift_input_entry = tk.Entry(tab2, width=50)
shift_input_entry.grid(row=1, column=1)
tk.Button(tab2, text="Browse", command=lambda: browse_file(shift_input_entry)).grid(row=1, column=2)

tk.Label(tab2, text="Output VTT").grid(row=2, column=0)
shift_output_entry = tk.Entry(tab2, width=50)
shift_output_entry.grid(row=2, column=1)
tk.Button(tab2, text="Browse", command=lambda: browse_file(shift_output_entry)).grid(row=2, column=2)

tk.Label(tab2, text="Shift (seconds)").grid(row=3, column=0)
shift_seconds_entry = tk.Entry(tab2)
shift_seconds_entry.grid(row=3, column=1)

tk.Button(tab2, text="Run VTT Shift", command=run_vtt_shift).grid(row=4, column=1)

# Combine
tk.Label(tab2, text="Combine VTT Files").grid(row=5, column=1)
tk.Label(tab2, text="VTT File 1").grid(row=6, column=0)
combine_vtt1_entry = tk.Entry(tab2, width=50)
combine_vtt1_entry.grid(row=6, column=1)
tk.Button(tab2, text="Browse", command=lambda: browse_file(combine_vtt1_entry)).grid(row=6, column=2)

tk.Label(tab2, text="VTT File 2").grid(row=7, column=0)
combine_vtt2_entry = tk.Entry(tab2, width=50)
combine_vtt2_entry.grid(row=7, column=1)
tk.Button(tab2, text="Browse", command=lambda: browse_file(combine_vtt2_entry)).grid(row=7, column=2)

tk.Label(tab2, text="Output VTT").grid(row=8, column=0)
combine_output_entry = tk.Entry(tab2, width=50)
combine_output_entry.grid(row=8, column=1)
tk.Button(tab2, text="Browse", command=lambda: browse_file(combine_output_entry)).grid(row=8, column=2)

tk.Label(tab2, text="Ep1 Duration (sec)").grid(row=9, column=0)
ep1_duration_entry = tk.Entry(tab2)
ep1_duration_entry.grid(row=9, column=1)

tk.Button(tab2, text="Run VTT Combine", command=run_vtt_combine).grid(row=10, column=1)

# --- Log Output ---
tab_control.pack(expand=1, fill='both')

log_text = tk.Text(root, height=10, bg="black", fg="lime")
log_text.pack(fill='both', expand=True)

root.mainloop()
