import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the directory containing obsm_calculator.py to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tool.obsm_calculator import SpellMaker

spell_maker = SpellMaker(skills={"Alteration": 5, "Conjuration": 5, "Destruction": 5, "Illusion": 5, "Mysticism": 5, "Restoration": 5})

def has_details(eff_name):
    return "Skill" in eff_name or "Attribute" in eff_name

def has_dur_only(eff_name):
    # Check if effect name includes "Bound" or "Summon" exactly or as substring
    return any(word in eff_name for word in ["Bound", "Summon", "Night"])

def create_main_buttons(scrollable_frame, right_frame, button_dict, canvas):
    for group, labels in button_dict.items():
        # Container for the whole group
        group_container = ttk.Frame(scrollable_frame)
        group_container.pack(fill="x", pady=5)

        # Group header
        header = ttk.Frame(group_container)
        header.pack(fill="x")

        header_label = ttk.Label(header, text=f"▼ {group}", font=("Segoe UI", 10, "bold"))
        header_label.pack(side="left", padx=5)

        # Frame that holds the effect buttons
        inner_frame = ttk.Frame(group_container)
        inner_frame.pack(fill="x", padx=10)

        # Toggle collapse/expand
        def toggle(event, header_label=header_label, inner_frame=inner_frame, group=group):
            if inner_frame.winfo_manager():
                inner_frame.pack_forget()
                header_label.config(text=f"▶ {group}")
            else:
                inner_frame.pack(fill="x", padx=10)  # no 'after=header'
                header_label.config(text=f"▼ {group}")

        header_label.bind("<Button-1>", toggle)

        # Create buttons for each effect
        for label in labels:
            button = ttk.Button(inner_frame, text=label, command=lambda l=label: add_effect(scrollable_frame, right_frame, l))
            button.pack(fill="x", pady=1)

def refresh_buttons():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    grouped = sort_effects_grouped(button_labels, sort_mode.get())
    create_main_buttons(scrollable_frame, right_frame, grouped, canvas)

def add_effect(left_frame, right_frame, clicked_text):
    # Clear entire left pane content first:
    for widget in left_frame.winfo_children():
        widget.destroy()
    # Continue
    widgets = []
    slider_data = []
    dropdown_value = tk.StringVar(value="Choose one..")
    range_value = tk.StringVar(value="Self")

    dur_only = has_dur_only(clicked_text)

    slider_ranges = {
        "Magnitude": (3, 100),
        "Duration": (1, 100),
        "Area": (0, 100),
    }

    # Only show Duration slider plus Magnitude and Area if NOT Bound or Summon
    sliders_to_show = ["Duration"]
    if not dur_only:
        sliders_to_show = ["Magnitude", "Duration", "Area"]

    for label in sliders_to_show:
        min_val, max_val = slider_ranges[label]

        lbl = ttk.Label(left_frame, text=label)
        lbl.pack()
        frame = ttk.Frame(left_frame)
        frame.pack(fill='x', pady=2)

        var = tk.StringVar()
        entry = ttk.Entry(frame, width=5, textvariable=var)
        entry.pack(side='left')

        def step(delta, label, var, scale):
            try:
                current = int(var.get())
                new_val = current + delta
                if label == "Area":
                    new_val = round(new_val / 5) * 5
                new_val = max(slider_ranges[label][0], min(slider_ranges[label][1], new_val))
                var.set(new_val)
                if scale:
                    scale.set(new_val)
            except ValueError:
                var.set(slider_ranges[label][0])
                if scale:
                    scale.set(slider_ranges[label][0])

        minus_btn = ttk.Button(frame, text="-", width=2)
        minus_btn.pack(side='left', padx=(2, 2))

        s = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal')
        s.pack(side='left', fill='x', expand=True, padx=5)

        plus_btn = ttk.Button(frame, text="+", width=2)
        plus_btn.pack(side='left', padx=(2, 0))

        minus_btn.config(command=lambda v=var, sc=s, lbl=label: step(-1, label=lbl, var=v, scale=sc))
        plus_btn.config(command=lambda v=var, sc=s, lbl=label: step(1, label=lbl, var=v, scale=sc))

        def slider_to_entry(val, var=var, label=label):
            val_int = int(float(val))
            if label == "Area":
                val_int = round(val_int / 5) * 5
            var.set(str(val_int))
        s.config(command=slider_to_entry)

        debounce_timers = {}

        def debounced_validate(var=var, min_val=min_val, max_val=max_val, scale=s, label=label):
            try:
                v = int(var.get())
                if label == "Area":
                    v = round(v / 5) * 5
                if v < min_val:
                    v = min_val
                elif v > max_val:
                    v = max_val
                var.set(str(v))
                scale.set(v)
            except ValueError:
                var.set(str(min_val))
                scale.set(min_val)

        def on_entry_change(event, var=var, min_val=min_val, max_val=max_val, scale=s, label=label):
            key = str(entry)
            if key in debounce_timers:
                entry.after_cancel(debounce_timers[key])
            debounce_timers[key] = entry.after(500, lambda: debounced_validate(var, min_val, max_val, scale, label))

        entry.bind("<KeyRelease>", on_entry_change)
        entry.bind("<FocusOut>", lambda e: debounced_validate(var, min_val, max_val, scale, label))

        var.set(str(min_val))
        s.set(min_val)

        slider_data.append((var, s))
        widgets.extend([lbl, frame])

    def save():
        try:
            # If Bound/Summon, no magnitude or area sliders
            if dur_only:
                # Magnitude and Area params are ignored or default
                params = {
                    "mag": 0,
                    "dur": int(slider_data[0][0].get()),  # only Duration slider data is present
                    "area": 0,
                    "range": range_value.get()
                }
            else:
                params = {
                    "mag": int(slider_data[0][0].get()),
                    "dur": int(slider_data[1][0].get()),
                    "area": int(slider_data[2][0].get()),
                    "range": range_value.get()
                }
            if has_dropdown:
                params["details"] = dropdown_value.get()

            spell_maker.update_spell(clicked_text, **params)
            update_saved_display(right_frame)
            cancel()
        except ValueError:
            pass

    # Save button declared here to work with disable logic
    save_button = ttk.Button(left_frame, text="Save", command=save)

    has_dropdown = has_details(clicked_text)
    if has_dropdown:
        dropdown_label = ttk.Label(left_frame, text="Select an option:")
        dropdown_label.pack()

        # Add "Choose one.." to the front of the list
        if "Attribute" in clicked_text:
            dropdown_options = ["Choose one..", "Strength", "Intelligence", "Willpower", "Agility", "Speed",
                                "Endurance", "Personality", "Luck"]
        else:
            dropdown_options = ["Choose one..", "Armorer", "Athletics", "Blade", "Block", "Blunt", "Hand to Hand",
                                "Heavy Armor",
                                "Alchemy", "Alteration", "Conjuration", "Destruction", "Illusion", "Mysticism",
                                "Restoration",
                                "Acrobatics", "Light Armor", "Marksman", "Mercantile", "Security", "Sneak",
                                "Speechcraft"]

        dropdown = ttk.Combobox(left_frame, textvariable=dropdown_value, values=dropdown_options, state="readonly")
        dropdown.current(0)  # Set default to "Choose one.."
        dropdown.pack()

        def on_dropdown_change(event):
            selected = dropdown.get()
            if selected != "Choose one..":
                save_button.config(state="normal")
            else:
                save_button.config(state="disabled")

        dropdown.bind("<<ComboboxSelected>>", on_dropdown_change)

        # Disable Save initially since default is "Choose one.."
        save_button.config(state="disabled")

        widgets.extend([dropdown_label, dropdown])

    range_label = ttk.Label(left_frame, text="Range:")
    range_label.pack()
    range_dropdown = ttk.Combobox(left_frame, textvariable=range_value)

    if dur_only:
        # Limit to only "Self" and readonly
        range_dropdown['values'] = ("Self",)
        range_value.set("Self")
        range_dropdown.state(["readonly"])
    elif "Absorb" in clicked_text:
        range_dropdown['values'] = ("Touch",)
        range_value.set("Touch")
        range_dropdown.state(["readonly"])
    else:
        range_dropdown['values'] = ("Touch", "Self", "Target")

    range_dropdown.pack()

    widgets.extend([range_label, range_dropdown])

    def cancel():
        for widget in widgets:
            widget.destroy()
        save_button.destroy()
        cancel_button.destroy()
        refresh_buttons()

    # Save packed here after options
    save_button.pack(pady=5)

    cancel_button = ttk.Button(left_frame, text="Cancel", command=cancel)
    cancel_button.pack(pady=5)

    left_frame.main_buttons = [save_button, cancel_button]
    canvas.yview_moveto(0)

def update_saved_display(right_frame):
    for widget in skills_frame.winfo_children():
        widget.destroy()

    debounce_timers = {}

    def on_skill_change(skill_name, var):
        def delayed_update():
            try:
                new_val = int(var.get())
                spell_maker.skills[skill_name] = new_val
                spell_maker.casting_cost = spell_maker._calc_cost()
                update_saved_display(right_frame)
            except ValueError:
                pass

        if skill_name in debounce_timers:
            right_frame.after_cancel(debounce_timers[skill_name])
        debounce_timers[skill_name] = right_frame.after(500, delayed_update)  # 500 ms delay

    if spell_maker.skills:
        skills = list(spell_maker.skills.items())
        for i, (skill, value) in enumerate(skills):
            row = i // 3
            col = i % 3

            frame = ttk.Frame(skills_frame)
            frame.grid(row=row, column=col, padx=5, pady=2, sticky='w')

            label = ttk.Label(frame, text=f"{skill}:")
            label.pack(side='left')

            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(frame, textvariable=var, width=5)
            entry.pack(side='left')

            var.trace_add("write", lambda *_, sk=skill, v=var: on_skill_change(sk, v))
    else:
        ttk.Label(skills_frame, text="No skills set.").pack(anchor='w')

    for widget in summary_frame.winfo_children():
        widget.destroy()

    if spell_maker.current_spell:
        ttk.Label(summary_frame, text=str(spell_maker.current_spell), justify='left').pack(anchor='w')

        # Add casting cost (modified by skill)
        cost_label = ttk.Label(summary_frame, text=f"Casting Cost (Skill Modified): {spell_maker.casting_cost:.2f}")
        cost_label.pack(anchor='w')
    else:
        ttk.Label(summary_frame, text="No spell created.").pack(anchor='w')

    for widget in right_frame.winfo_children():
        widget.destroy()

    if not spell_maker.current_spell or not spell_maker.current_spell.effects:
        ttk.Label(right_frame, text="No effects in spell.").pack()
        return

    for idx, eff in enumerate(spell_maker.current_spell.effects):
        frame = ttk.Frame(right_frame)
        frame.pack(fill='x', pady=2, padx=5)

        label = ttk.Label(frame, text=str(eff))
        label.pack(side='left', expand=True, anchor='w')

        edit_btn = ttk.Button(frame, text="Edit", command=lambda i=idx: edit_entry(i, right_frame, scrollable_frame))
        edit_btn.pack(side='right', padx=2)

        delete_btn = ttk.Button(frame, text="Delete", command=lambda i=idx: delete_entry(i, right_frame))
        delete_btn.pack(side='right', padx=2)

def edit_entry(index, right_frame, left_frame):
    eff = spell_maker.current_spell.effects[index]

    main_window = right_frame.winfo_toplevel()
    edit_win = tk.Toplevel(main_window)
    edit_win.geometry("300x350")
    edit_win.transient(main_window)
    edit_win.grab_set()

    update_timer = None

    def debounced_apply_update():
        nonlocal update_timer
        if update_timer:
            edit_win.after_cancel(update_timer)
        update_timer = edit_win.after(100, apply_live_update)

    def center_edit_window():
        right_x = right_frame.winfo_rootx()
        right_y = right_frame.winfo_rooty()
        right_w = right_frame.winfo_width()
        right_h = right_frame.winfo_height()

        win_w = 300
        win_h = 350

        # Position just to the right of the right frame
        pos_x = right_x + right_w + 5  # 5 px padding
        pos_y = right_y + (right_h // 2) - (win_h // 2)

        edit_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    main_window.update_idletasks()
    center_edit_window()

    last_pos = {"x": main_window.winfo_x(), "y": main_window.winfo_y()}

    def safe_center(event):
        if not edit_win.winfo_exists():
            return

        new_x = main_window.winfo_x()
        new_y = main_window.winfo_y()

        # Only re-center if window moved (not resized)
        if new_x != last_pos["x"] or new_y != last_pos["y"]:
            last_pos["x"] = new_x
            last_pos["y"] = new_y
            center_edit_window()

    main_window.bind("<Configure>", safe_center)

    title_bar = tk.Frame(edit_win, bg="#444")
    title_bar.pack(fill="x")
    title_label = tk.Label(title_bar, text="Edit Effect", bg="#444", fg="white")
    title_label.pack(padx=10, pady=5)

    content_frame = ttk.Frame(edit_win)
    content_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ttk.Label(content_frame, text=f"Effect: {eff.name}").pack(pady=5)

    slider_ranges = {
        "Magnitude": (3, 100),
        "Duration": (1, 100),
        "Area": (0, 100),
    }

    dur_only = has_dur_only(eff.name)
    sliders_to_show = ["Duration"] if dur_only else ["Magnitude", "Duration", "Area"]
    label_to_attr = {"Magnitude": "mag", "Duration": "dur", "Area": "area"}

    def apply_live_update():
        try:
            params = {}
            if dur_only:
                params = {"mag": 0, "area": 0, "dur": dur_var.get()}
            else:
                params = {
                    "mag": mag_var.get(),
                    "dur": dur_var.get(),
                    "area": round(area_var.get() / 5) * 5
                }
            params["range"] = range_value.get()
            if has_details(eff.name):
                params["details"] = dropdown_var.get()

            spell_maker.update_spell(eff.name, **params)
            update_saved_display(right_frame)
        except (ValueError, tk.TclError):
            pass

    # Initialize variables and trace
    var_dict = {}
    for label in sliders_to_show:
        attr = label_to_attr[label]
        val = getattr(eff, attr)
        min_val, max_val = slider_ranges[label]

        ttk.Label(content_frame, text=label).pack()
        frame = ttk.Frame(content_frame)
        frame.pack(fill='x', pady=2)

        var = tk.IntVar(value=val)
        var.trace_add("write", lambda *args: debounced_apply_update())
        var_dict[label] = var

        entry = ttk.Entry(frame, width=5, textvariable=var)
        entry.pack(side='left')

        # Define stepper logic
        def step(delta, label, var, scale):
            try:
                current = int(var.get())
                new_val = current + delta
                if label == "Area":
                    new_val = round(new_val / 5) * 5
                new_val = max(slider_ranges[label][0], min(slider_ranges[label][1], new_val))
                var.set(new_val)
                if scale:
                    scale.set(new_val)
            except ValueError:
                var.set(slider_ranges[label][0])
                if scale:
                    scale.set(slider_ranges[label][0])

        minus_btn = ttk.Button(frame, text="-", width=2)
        minus_btn.pack(side='left', padx=(2, 2))

        s = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal')
        s.set(val)
        s.pack(side='left', fill='x', expand=True, padx=5)

        plus_btn = ttk.Button(frame, text="+", width=2)
        plus_btn.pack(side='left', padx=(2, 0))

        # Connect events
        def on_slider_change(val, var=var):
            var.set(int(float(val)))
            debounced_apply_update()

        s.config(command=on_slider_change)
        minus_btn.config(command=lambda v=var, sc=s, lbl=label: step(-1, label=lbl, var=v, scale=sc))
        plus_btn.config(command=lambda v=var, sc=s, lbl=label: step(1, label=lbl, var=v, scale=sc))

    mag_var = var_dict.get("Magnitude", tk.IntVar(value=0))
    dur_var = var_dict.get("Duration", tk.IntVar(value=1))
    area_var = var_dict.get("Area", tk.IntVar(value=0))

    range_value = tk.StringVar(value=eff.range)
    range_value.trace_add("write", lambda *args: debounced_apply_update())
    ttk.Label(content_frame, text="Range:").pack()
    range_dropdown = ttk.Combobox(content_frame, textvariable=range_value)
    if dur_only:
        range_dropdown['values'] = ("Self",)
        range_value.set("Self")
        range_dropdown.state(["readonly"])
    elif "Absorb" in eff.name:
        range_dropdown['values'] = ("Touch",)
        range_value.set("Touch")
        range_dropdown.state(["readonly"])
    else:
        range_dropdown['values'] = ("Touch", "Self", "Target")
    range_dropdown.pack()

    dropdown_var = tk.StringVar(value=eff.details)
    if has_details(eff.name):
        dropdown_var.trace_add("write", lambda *args: debounced_apply_update())
        ttk.Label(content_frame, text="Details:").pack()
        ddl = ttk.Combobox(content_frame, textvariable=dropdown_var)
        if "Attribute" in eff.name:
            ddl['values'] = ("Strength", "Intelligence", "Willpower", "Agility", "Speed", "Endurance", "Personality", "Luck")
        else:
            ddl['values'] = ("Armorer", "Athletics", "Blade", "Block", "Blunt", "Hand to Hand", "Heavy Armor",
                             "Alchemy", "Alteration", "Conjuration", "Destruction", "Illusion", "Mysticism", "Restoration",
                             "Acrobatics", "Light Armor", "Marksman", "Mercantile", "Security", "Sneak", "Speechcraft")
        ddl.pack()

def delete_entry(index, right_frame):
    eff = spell_maker.current_spell.effects[index]
    spell_maker.current_spell.remove_effect(eff.name, eff.details)
    update_saved_display(right_frame)

# === GUI Initialization ===
root = tk.Tk()
root.title("Spell Maker")
root.geometry("800x500")
style = ttk.Style()
style.configure("Header.TButton", font=("Segoe UI", 10, "bold"))

paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

sort_mode = tk.StringVar(value="Alphabetical")

def sort_effects_grouped(labels, mode):
    if mode == "Alphabetical":
        grouped = {"A–Z": sorted(labels)}
    elif mode == "By School":
        grouped = {}
        for label in labels:
            school = spell_maker.get_effect_school(label) or "Unknown"
            grouped.setdefault(school, []).append(label)
        for k in grouped:
            grouped[k].sort()
    elif mode == "By Function":
        grouped = {}
        for label in labels:
            function = spell_maker.get_effect_function(label) or "Unknown"
            grouped.setdefault(function, []).append(label)
        for k in grouped:
            grouped[k].sort()
    else:
        grouped = {"All": labels}
    return dict(sorted(grouped.items()))  # Sort groups alphabetically or numerically


left_outer = ttk.Frame(paned, width=170)
left_outer.pack_propagate(False)

canvas = tk.Canvas(left_outer, borderwidth=0, width=150)
scrollbar = ttk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

sort_frame = ttk.Frame(left_outer)
sort_frame.pack(fill='x', pady=5)

ttk.Label(sort_frame, text="Sort by:").pack(side='left', padx=(5, 2))

sort_dropdown = ttk.OptionMenu(
    sort_frame, sort_mode, sort_mode.get(),
    "Alphabetical", "By School", "By Function",
    command=lambda _: refresh_buttons()
)
sort_dropdown.pack(side='left', padx=2)


canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
scrollable_frame.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
scrollable_frame.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

paned.add(left_outer, weight=1)

right_container = ttk.Frame(paned)
right_container.pack(fill=tk.BOTH, expand=True)

skills_frame = ttk.Frame(right_container, relief=tk.GROOVE, padding=5)
skills_frame.pack(fill='x')

right_frame = ttk.Frame(right_container, relief=tk.SUNKEN)
right_frame.pack(fill='both', expand=True)

summary_frame = ttk.Frame(right_container, relief=tk.GROOVE, padding=5)
summary_frame.pack(fill='x')

paned.add(right_container, weight=5)

button_labels = spell_maker.df["Effect Name"].dropna().unique().tolist()
sorted_labels = sort_effects_grouped(button_labels, sort_mode.get())
create_main_buttons(scrollable_frame, right_frame, sorted_labels, canvas)
update_saved_display(right_frame)

root.mainloop()
