import tkinter as tk
from tkinter import ttk
from obsm_calculator import SpellMaker

spell_maker = SpellMaker(skills={"Alteration": 5, "Conjuration": 5, "Destruction": 5, "Illusion": 5, "Mysticism": 5, "Restoration": 5})

def has_details(eff_name):
    return "Skill" in eff_name or "Attribute" in eff_name

def is_bound_or_summon(eff_name):
    # Check if effect name includes "Bound" or "Summon" exactly or as substring
    return any(word in eff_name for word in ["Bound", "Summon"])

def create_main_buttons(left_frame, right_frame, labels, canvas):
    buttons = []
    left_frame.main_buttons = buttons

    def on_button_click(label_text):
        for btn in buttons:
            btn.destroy()
        canvas.yview_moveto(0)
        clicked_label = ttk.Label(left_frame, text=f"{label_text}")
        clicked_label.pack(pady=10)
        create_sliders_save_cancel(left_frame, right_frame, labels, clicked_label, label_text)

    for label_text in labels:
        button = ttk.Button(left_frame, text=label_text)
        button.config(command=lambda t=label_text: on_button_click(t))
        button.pack(pady=5)
        buttons.append(button)

def create_sliders_save_cancel(left_frame, right_frame, labels, clicked_label, clicked_text):
    widgets = [clicked_label]
    slider_data = []
    dropdown_value = tk.StringVar(value="Choose one..")
    range_value = tk.StringVar(value="Self")

    is_bound_or_summon = ("Bound" in clicked_text) or ("Summon" in clicked_text)

    slider_ranges = {
        "Magnitude": (3, 100),
        "Duration": (1, 100),
        "Area": (0, 100),
    }

    # Only show Duration slider plus Magnitude and Area if NOT Bound or Summon
    sliders_to_show = ["Duration"]
    if not is_bound_or_summon:
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

        s = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal')
        s.pack(side='left', fill='x', expand=True, padx=5)

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

    has_dropdown = has_details(clicked_text)
    if has_dropdown:
        dropdown_label = ttk.Label(left_frame, text="Select an option:")
        dropdown_label.pack()
        dropdown = ttk.Combobox(left_frame, textvariable=dropdown_value)
        if "Attribute" in clicked_text:
            dropdown['values'] = ("Strength", "Intelligence", "Willpower", "Agility", "Speed", "Endurance", "Personality", "Luck")
        else:
            dropdown['values'] = ("Armorer", "Athletics", "Blade", "Block", "Blunt", "Hand to Hand", "Heavy Armor",
                                   "Alchemy", "Alteration", "Conjuration", "Destruction", "Illusion", "Mysticism", "Restoration",
                                   "Acrobatics", "Light Armor", "Marksman", "Mercantile", "Security", "Sneak", "Speechcraft")
        dropdown.pack()
        widgets.extend([dropdown_label, dropdown])

    range_label = ttk.Label(left_frame, text="Range:")
    range_label.pack()
    range_dropdown = ttk.Combobox(left_frame, textvariable=range_value)

    if is_bound_or_summon:
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
        create_main_buttons(left_frame, right_frame, labels, canvas)

    def save():
        try:
            # If Bound/Summon, no magnitude or area sliders
            if is_bound_or_summon:
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

    save_button = ttk.Button(left_frame, text="Save", command=save)
    save_button.pack(pady=5)

    cancel_button = ttk.Button(left_frame, text="Cancel", command=cancel)
    cancel_button.pack(pady=5)

    left_frame.main_buttons = [save_button, cancel_button]

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

    def center_edit_window():
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        main_w = main_window.winfo_width()
        main_h = main_window.winfo_height()
        win_w = 300
        win_h = 350
        pos_x = main_x + (main_w // 2) - (win_w // 2)
        pos_y = main_y + (main_h // 2) - (win_h // 2)
        edit_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    main_window.update_idletasks()
    center_edit_window()

    def safe_center(e):
        if edit_win.winfo_exists():
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

    bound_or_summon = is_bound_or_summon(eff.name)

    # Only Duration slider for Bound/Summon effects
    sliders_to_show = ["Duration"] if bound_or_summon else ["Magnitude", "Duration", "Area"]

    label_to_attr = {
        "Magnitude": "mag",
        "Duration": "dur",
        "Area": "area"
    }
    vars_ = []
    for label in sliders_to_show:
        val = getattr(eff, label_to_attr[label])
        min_val, max_val = slider_ranges[label]

        ttk.Label(content_frame, text=label).pack()
        frame = ttk.Frame(content_frame)
        frame.pack(fill='x', pady=2)

        var = tk.StringVar(value=str(val))
        entry = ttk.Entry(frame, width=5, textvariable=var)
        entry.pack(side='left')

        s = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal')
        s.config(command=lambda val, var=var: var.set(str(int(float(val)))))
        s.pack(side='left', fill='x', expand=True, padx=5)

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

        s.set(val)
        vars_.append(var)

    range_value = tk.StringVar(value=eff.range)
    ttk.Label(content_frame, text="Range:").pack()
    range_dropdown = ttk.Combobox(content_frame, textvariable=range_value)
    if bound_or_summon:
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
        ttk.Label(content_frame, text="Details:").pack()
        ddl = ttk.Combobox(content_frame, textvariable=dropdown_var)
        if "Attribute" in eff.name:
            ddl['values'] = ("Strength", "Intelligence", "Willpower", "Agility", "Speed", "Endurance", "Personality", "Luck")
        else:
            ddl['values'] = ("Armorer", "Athletics", "Blade", "Block", "Blunt", "Hand to Hand", "Heavy Armor",
                             "Alchemy", "Alteration", "Conjuration", "Destruction", "Illusion", "Mysticism", "Restoration",
                             "Acrobatics", "Light Armor", "Marksman", "Mercantile", "Security", "Sneak", "Speechcraft")
        ddl.pack()
    else:
        ddl = None

    def cancel_edit():
        edit_win.destroy()

    def save_edit():
        try:
            if bound_or_summon:
                mag = 0
                dur = int(vars_[0].get())
                area = 0
            else:
                mag = int(vars_[0].get())
                dur = int(vars_[1].get())
                area = int(vars_[2].get())

            rng = range_value.get()
            det = dropdown_var.get() if has_details(eff.name) else ""

            params = {
                "mag": mag,
                "dur": dur,
                "area": area,
                "range": rng
            }
            if det:
                params["details"] = det

            effect_name = spell_maker.current_spell.effects[index].name
            spell_maker.update_spell(effect_name, **params)

            update_saved_display(right_frame)
            edit_win.destroy()
        except ValueError:
            pass

    btn_frame = ttk.Frame(edit_win)
    btn_frame.pack(fill='x', pady=10)

    ttk.Button(btn_frame, text="Save", command=save_edit).pack(side='left', expand=True)
    ttk.Button(btn_frame, text="Cancel", command=cancel_edit).pack(side='left', expand=True)

def delete_entry(index, right_frame):
    eff = spell_maker.current_spell.effects[index]
    spell_maker.current_spell.remove_effect(eff.name, eff.details)
    update_saved_display(right_frame)

# === GUI Initialization ===
root = tk.Tk()
root.title("Spell Maker")
root.geometry("800x400")

paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

left_outer = ttk.Frame(paned, width=150)
left_outer.pack_propagate(False)

canvas = tk.Canvas(left_outer, borderwidth=0, width=150)
scrollbar = ttk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

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
create_main_buttons(scrollable_frame, right_frame, button_labels, canvas)
update_saved_display(right_frame)

root.mainloop()
