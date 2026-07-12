"""Tkinter GUI for the subtitle toolkit.

Imports the core library directly (no subprocess), runs jobs on a worker
thread so the window stays responsive, and streams progress into a log pane.
"""

import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from subtitle_toolkit.burn import burn_subtitles, mux_subtitles
from subtitle_toolkit.cli import _resolve_output
from subtitle_toolkit.matching import find_matching_pairs
from subtitle_toolkit.vtt import combine_vtt, shift_vtt


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Subtitle Toolkit")

        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self.worker = None
        self.run_buttons = []

        notebook = ttk.Notebook(root)
        self._build_video_tab(notebook)
        self._build_vtt_tab(notebook)
        notebook.pack(expand=1, fill="both")

        self.log_text = tk.Text(root, height=12, bg="black", fg="lime")
        self.log_text.pack(fill="both", expand=True)

        root.after(100, self._drain_log)

    # ----- widget helpers -------------------------------------------------

    def _path_row(self, parent, row, label, mode):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
        entry = tk.Entry(parent, width=55)
        entry.grid(row=row, column=1, padx=4)

        def browse():
            if mode == "open":
                path = filedialog.askopenfilename()
            elif mode == "save":
                path = filedialog.asksaveasfilename()
            else:
                path = filedialog.askdirectory()
            if path:
                entry.delete(0, tk.END)
                entry.insert(0, path)

        tk.Button(parent, text="Browse", command=browse).grid(row=row, column=2, padx=4)
        return entry

    def _run_button(self, parent, row, label, job):
        button = tk.Button(parent, text=label, command=lambda: self._start_job(job))
        button.grid(row=row, column=1, pady=6)
        self.run_buttons.append(button)
        return button

    # ----- tabs -----------------------------------------------------------

    def _build_video_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Video + Subtitles")

        self.video_entry = self._path_row(tab, 0, "Video (file or folder)", "open")
        self.sub_entry = self._path_row(tab, 1, "Subtitles (file or folder)", "open")
        self.output_entry = self._path_row(tab, 2, "Output (file or folder)", "save")

        options = ttk.Frame(tab)
        options.grid(row=3, column=1, sticky="w")

        tk.Label(options, text="Offset (s)").pack(side="left")
        self.offset_entry = tk.Entry(options, width=8)
        self.offset_entry.insert(0, "0")
        self.offset_entry.pack(side="left", padx=(2, 10))

        tk.Label(options, text="Position").pack(side="left")
        self.position_var = tk.StringVar(value="top")
        ttk.Combobox(
            options, textvariable=self.position_var, values=["top", "bottom"],
            width=8, state="readonly",
        ).pack(side="left", padx=(2, 10))

        self.debug_var = tk.BooleanVar()
        tk.Checkbutton(options, text="Debug (first minute)", variable=self.debug_var).pack(side="left")

        self._run_button(tab, 4, "Burn (hardcode, re-encodes)", self._job_burn)
        self._run_button(tab, 5, "Mux (soft track, fast)", self._job_mux)

    def _build_vtt_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="VTT Tools")

        tk.Label(tab, text="Shift timings", font=("", 10, "bold")).grid(
            row=0, column=1, pady=(6, 0))
        self.shift_input = self._path_row(tab, 1, "Input VTT", "open")
        self.shift_output = self._path_row(tab, 2, "Output VTT", "save")
        tk.Label(tab, text="Shift (seconds)").grid(row=3, column=0, sticky="w", padx=4)
        self.shift_seconds = tk.Entry(tab, width=10)
        self.shift_seconds.grid(row=3, column=1, sticky="w", padx=4)
        self._run_button(tab, 4, "Run Shift", self._job_shift)

        tk.Label(tab, text="Combine two files", font=("", 10, "bold")).grid(
            row=5, column=1, pady=(12, 0))
        self.combine_vtt1 = self._path_row(tab, 6, "VTT File 1", "open")
        self.combine_vtt2 = self._path_row(tab, 7, "VTT File 2", "open")
        self.combine_output = self._path_row(tab, 8, "Output VTT", "save")
        tk.Label(tab, text="File 1 duration (s)").grid(row=9, column=0, sticky="w", padx=4)
        self.ep1_duration = tk.Entry(tab, width=10)
        self.ep1_duration.grid(row=9, column=1, sticky="w", padx=4)
        self._run_button(tab, 10, "Run Combine", self._job_combine)

    # ----- jobs (run on the worker thread) ---------------------------------

    def _for_each_pair(self, action):
        pairs, unmatched = find_matching_pairs(
            self.video_entry.get(), self.sub_entry.get())
        for video in unmatched:
            self.log(f"Warning: no matching subtitle for {video}")
        if not pairs:
            self.log("No matching video/subtitle pairs found.")
            return
        single = len(pairs) == 1
        for video, sub in pairs:
            out_file = _resolve_output(video, self.output_entry.get(), single)
            self.log(f"{video} + {sub} -> {out_file}")
            action(video, sub, out_file)
            self.log(f"Done: {out_file}")

    def _job_burn(self):
        offset = float(self.offset_entry.get() or 0)
        limit = 60 if self.debug_var.get() else None
        self._for_each_pair(
            lambda video, sub, out: burn_subtitles(
                video, sub, out,
                time_offset=offset,
                position=self.position_var.get(),
                limit_seconds=limit,
                progress=self.log,
            )
        )

    def _job_mux(self):
        self._for_each_pair(
            lambda video, sub, out: mux_subtitles(video, sub, out, progress=self.log)
        )

    def _job_shift(self):
        count = shift_vtt(
            self.shift_input.get(), self.shift_output.get(),
            float(self.shift_seconds.get()))
        self.log(f"Wrote {count} cues to {self.shift_output.get()}")

    def _job_combine(self):
        count = combine_vtt(
            self.combine_vtt1.get(), self.combine_vtt2.get(),
            self.combine_output.get(), float(self.ep1_duration.get()))
        self.log(f"Wrote {count} cues to {self.combine_output.get()}")

    # ----- threading / logging ---------------------------------------------

    def _start_job(self, job):
        if self.worker and self.worker.is_alive():
            self.log("A job is already running.")
            return
        self.log_text.delete("1.0", tk.END)
        for button in self.run_buttons:
            button.config(state="disabled")

        def run():
            try:
                job()
            except Exception as exc:
                self.log(f"Error: {exc}")
            finally:
                self.log_queue.put(("__done__"))

        self.worker = threading.Thread(target=run, daemon=True)
        self.worker.start()

    def log(self, message: str):
        self.log_queue.put(message)

    def _drain_log(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                if message == "__done__":
                    for button in self.run_buttons:
                        button.config(state="normal")
                else:
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self._drain_log)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
