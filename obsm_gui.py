import tkinter as tk
from tkinter import ttk

saved_entries = []
edit_win = None

def create_main_buttons(left_frame, right_frame, labels):
    buttons = []
    left_frame.main_buttons = buttons

    def on_button_click(label_text):
        for btn in buttons:
            btn.destroy()
        clicked_label = ttk.Label(left_frame, text=f"You clicked: {label_text}")
        clicked_label.pack(pady=10)
        create_sliders_save_restart(left_frame, right_frame, labels, clicked_label, label_text)

    for label_text in labels:
        button = ttk.Button(left_frame, text=label_text)
        button.config(command=lambda t=label_text: on_button_click(t))
        button.pack(pady=5)
        buttons.append(button)

def create_sliders_save_restart(left_frame, right_frame, labels, clicked_label, clicked_text):
    widgets = [clicked_label]
    slider_data = []
    dropdown_value = tk.StringVar(value="Option 1")

    for i in range(3):
        label = ttk.Label(left_frame, text=f"Slider {i+1} value: 0")
        label.pack()
        slider = ttk.Scale(
            left_frame,
            from_=0,
            to=100,
            orient='horizontal',
            command=lambda val, l=label, idx=i: l.config(text=f"Slider {idx+1} value: {int(float(val))}")
        )
        slider.set(0)
        slider.pack()
        slider_data.append((label, slider))
        widgets.extend([label, slider])

    has_dropdown = "Attribute" in clicked_text or "Field" in clicked_text
    if has_dropdown:
        dropdown_label = ttk.Label(left_frame, text="Select an option:")
        dropdown_label.pack()
        dropdown = ttk.Combobox(left_frame, textvariable=dropdown_value)
        dropdown['values'] = ("Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6")
        dropdown.pack()
        widgets.extend([dropdown_label, dropdown])

    def restart():
        for widget in widgets:
            widget.destroy()
        save_button.destroy()
        restart_button.destroy()
        create_main_buttons(left_frame, right_frame, labels)

    def save():
        entry = {
            "Button": clicked_text,
            "Sliders": [int(slider.get()) for _, slider in slider_data],
            "Dropdown": dropdown_value.get() if has_dropdown else None
        }
        saved_entries.append(entry)
        update_saved_display(right_frame)
        restart()

    save_button = ttk.Button(left_frame, text="Save", command=save)
    save_button.pack(pady=5)

    restart_button = ttk.Button(left_frame, text="Restart", command=restart)
    restart_button.pack(pady=5)

    left_frame.main_buttons = [save_button, restart_button]

def update_saved_display(right_frame):
    for widget in right_frame.winfo_children():
        widget.destroy()

    if not saved_entries:
        ttk.Label(right_frame, text="No saved entries yet.").pack()
        return

    right_frame.edit_buttons = []
    right_frame.delete_buttons = []

    for idx, entry in enumerate(saved_entries):
        frame = ttk.Frame(right_frame)
        frame.pack(fill='x', pady=2, padx=5)

        text = f"{entry['Button']} - Sliders: {entry['Sliders']}"
        if entry["Dropdown"]:
            text += f" - Dropdown: {entry['Dropdown']}"
        label = ttk.Label(frame, text=text)
        label.pack(side='left', expand=True, anchor='w')

        edit_btn = ttk.Button(frame, text="Edit", command=lambda i=idx: edit_entry(i, right_frame, left_frame))
        edit_btn.pack(side='right', padx=2)
        right_frame.edit_buttons.append(edit_btn)

        delete_btn = ttk.Button(frame, text="Delete", command=lambda i=idx: delete_entry(i, right_frame))
        delete_btn.pack(side='right', padx=2)
        right_frame.delete_buttons.append(delete_btn)

def edit_entry(index, right_frame, left_frame):
    global edit_win
    entry = saved_entries[index]

    for btn in getattr(right_frame, 'edit_buttons', []):
        btn.config(state='disabled')
    for btn in getattr(right_frame, 'delete_buttons', []):
        btn.config(state='disabled')
    for btn in getattr(left_frame, 'main_buttons', []):
        btn.config(state='disabled')

    edit_win = tk.Toplevel()
    edit_win.geometry("300x350")
    edit_win.transient(right_frame.winfo_toplevel())
    edit_win.grab_set()

    main_win = right_frame.winfo_toplevel()
    main_win.update_idletasks()
    win_w, win_h = 300, 350

    def center_edit_window():
        if edit_win and edit_win.winfo_exists():
            main_x = main_win.winfo_x()
            main_y = main_win.winfo_y()
            main_w = main_win.winfo_width()
            main_h = main_win.winfo_height()
            new_x = main_x + (main_w - win_w) // 2
            new_y = main_y + (main_h - win_h) // 2
            edit_win.geometry(f"{win_w}x{win_h}+{new_x}+{new_y}")

    center_edit_window()
    main_win.bind("<Configure>", lambda e: center_edit_window())

    title_bar = tk.Frame(edit_win, bg="#444", relief="raised", bd=0)
    title_bar.pack(fill="x")
    title_label = tk.Label(title_bar, text="Edit Window", bg="#444", fg="white")
    title_label.pack(padx=10, pady=5)

    content_frame = ttk.Frame(edit_win)
    content_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ttk.Label(content_frame, text=f"Button Label: {entry['Button']}").pack(pady=5)

    slider_vars = []
    for i, val in enumerate(entry["Sliders"]):
        var = tk.IntVar(value=val)
        label = ttk.Label(content_frame, text=f"Slider {i+1} value: {val}")
        label.pack()
        slider = ttk.Scale(
            content_frame,
            from_=0,
            to=100,
            orient='horizontal',
            variable=var,
            command=lambda val, l=label, idx=i: l.config(text=f"Slider {idx+1} value: {int(float(val))}")
        )
        slider.pack()
        slider_vars.append(var)

    dropdown_var = tk.StringVar(value=entry["Dropdown"])
    if entry["Dropdown"]:
        dropdown_label = ttk.Label(content_frame, text="Select an option:")
        dropdown_label.pack()
        dropdown = ttk.Combobox(content_frame, textvariable=dropdown_var)
        dropdown['values'] = ("Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6")
        dropdown.pack()

    def save_changes():
        entry["Sliders"] = [v.get() for v in slider_vars]
        if entry["Dropdown"]:
            entry["Dropdown"] = dropdown_var.get()
        update_saved_display(right_frame)
        on_close()

    def on_close():
        for btn in getattr(right_frame, 'edit_buttons', []):
            btn.config(state='normal')
        for btn in getattr(right_frame, 'delete_buttons', []):
            btn.config(state='normal')
        for btn in getattr(left_frame, 'main_buttons', []):
            btn.config(state='normal')
        edit_win.destroy()

    # Always show Save and Cancel buttons
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Cancel", command=on_close).pack(side='left', padx=5)

    edit_win.protocol("WM_DELETE_WINDOW", on_close)

def delete_entry(index, right_frame):
    del saved_entries[index]
    update_saved_display(right_frame)

# Initialize the GUI
root = tk.Tk()
root.title("Two-Pane Interactive GUI")
root.geometry("600x400")

paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

left_frame = ttk.Frame(paned, width=300, relief=tk.SUNKEN)
right_frame = ttk.Frame(paned, width=300, relief=tk.SUNKEN)

paned.add(left_frame, weight=1)
paned.add(right_frame, weight=1)

button_labels = ["Attribute1", "Field1", "Component1", "Parameter1"]
create_main_buttons(left_frame, right_frame, button_labels)

root.mainloop()
