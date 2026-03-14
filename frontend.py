import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox
from database import (
    autocomplete_art,
    add_art,
    get_or_create_fundort,
    add_beobachtung,
    last_beobachtungen,
    get_art_by_name,
    last_nadel,
    last_nadel_with_p
)

# ------------------------------------------------------------------------------------------------------------
# 0. Introduction
#
# - The frontend is made with tkinter with themes and fonts for better look
# - all information created in database.py has to get imported (see top)
#
# ------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------
# 1. Main window
# ------------------------------------------------------------------------------------------------------------

root = tk.Tk()
root.title("Arten & Beobachtungen") # add a title

# start the frontend in fullscreen:
root.update_idletasks()
root.geometry(
    f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0"
)

# ------------------------------------------------------------------------------------------------------------
# 2. Functions
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# 2.1 Help functions for empty fields
# ------------------------------------------------------------------------------------------------------------
selected_art_id = None

def to_int(value):
    value = value.strip()
    return int(value) if value else None

def to_float(value):
    value = value.strip()
    return float(value) if value else None


# ------------------------------------------------------------------------------------------------------------
# 2.2 Species autocompletion
#
# - on_keyrelease: recognizes typing and search for names
#
# - on_listbox_select: searches for names, preview all hits and adds the option to select the species
#
# ------------------------------------------------------------------------------------------------------------

def on_keyrelease(event):
    global selected_art_id, autocomplete_results
    selected_art_id = None
    listbox.delete(0, tk.END)
    autocomplete_results = []
    value = art_entry.get()
    if value:
        results = autocomplete_art(value)
        autocomplete_results = results
        for _, art in results:
            listbox.insert(tk.END, art)

def on_listbox_select(event):
    global selected_art_id
    if listbox.curselection():
        idx = listbox.curselection()[0]
        art_id, art = autocomplete_results[idx]  # here safe assignment
        selected_art_id = art_id
        art_entry.delete(0, tk.END)
        art_entry.insert(0, art)

# ------------------------------------------------------------------------------------------------------------
# 2.3 Save Button
#
# - creates a error message box if a species was not entered.
# - when new species name is recognized it enters a new species (see database.py chapter 1.1)
# - resetting certain fields
#
# ------------------------------------------------------------------------------------------------------------

def save_entry():
    global selected_art_id

    art_name = art_entry.get().strip()
    if not art_name:
        messagebox.showerror("Fehler", "Bitte Art eingeben")
        return

    # existing species -> no insert
    if selected_art_id is not None:
        art_id = selected_art_id

    # new species -> insert
    else:
        parts = art_name.split(maxsplit=1)
        if len(parts) != 2:
            messagebox.showerror(
                "Fehler",
                "Art bitte als 'Gattung Art' eingeben (z.B. Ceutorhynchus pallidactylus)"
            )
            return

        genus, species = parts

        # check, if a species exists
        art_id = get_art_by_name(genus, species)
        if art_id is None:
            art_id = add_art("", "", "", genus, species, "", "", "")

    # reset after saving the observation
    selected_art_id = None

    fundort_id = get_or_create_fundort(
        country.get(),
        region.get(),
        village.get(),
        location.get(),
        habitat.get(),
        to_float(lat.get()),
        to_float(lng.get()),
        to_float(height.get()),
        to_int(precision.get())
    )

    add_beobachtung(
        to_int(count.get()),
        date1.get(),
        date2.get(),
        method.get(),
        proof.get(),
        comment.get(),
        pcomment.get(),
        leg.get(),
        det.get(),
        vid.get(),
        coll.get(),
        fundort_id,
        art_id,
        nadel.get(),
        abg.get(),
        loan.get(),
        project.get(),
        eppi.get(),
        old.get(),
        ill.get(),
        new.get(),
        sex.get(),
        pic.get(),
    )

    update_preview() # update Nadel preview after savind the observation
    
    status.config(text=f"✔ Beobachtung gespeichert: {art_name}")
    show_last()
    clear_fields()

# ------------------------------------------------------------------------------------------------------------
# 2.4 Function for the table preview:
# ------------------------------------------------------------------------------------------------------------

def show_last():
    for item in tree.get_children():
        tree.delete(item)
    for row in last_beobachtungen():
        tree.insert("", "end", values=row)

# ------------------------------------------------------------------------------------------------------------
# 2.5 Refresh button
#
# This button is used when editing the database while using the frontend. In this case both programs access
# the database. To ensure you don't enter any double information or cause some bad error in the database you
# need to refresh.
# How to use:
# In case you edit information in DB Browser you need to save the database in DB Browser, switch to the
# frontend and click the Refresh button. In case you edited information displayed in the table preview this
# change should be visible now.
# In case you edit information in DB Browser and did not save your changes: if you switch back to the frontend
# and add a new observation the program gets stuck. You need to restart the frontend.
# ------------------------------------------------------------------------------------------------------------

def refresh_table():
    show_last()
    status.config(text="🔄 Tabelle aktualisiert")
    
# ------------------------------------------------------------------------------------------------------------
# 2.6 Dropdown selection
# ------------------------------------------------------------------------------------------------------------

def fc(parent, label, row, col, values, width=18, readonly=True):
    ttk.Label(parent, text=label).grid(
        row=row, column=col*2, sticky="e", padx=5, pady=3
    )
    cb = ttk.Combobox(
        parent,
        values=values,
        width=width,
        state="readonly" if readonly else "normal"
    )
    cb.grid(
        row=row, column=col*2+1, sticky="w", padx=5, pady=3
    )
    return cb

METHODEN = ["", "Streifkescher", "Klopfschirm", "Handaufsammlung", "Lichtfang / am Licht", "Gesiebe", "sonstige", "Hochwasser (Gesiebe)", "Bodenfalle", "Lufteklektor", "Sicht (Beobachtung)", "Zucht / ex Larva", "Farbschale"]

SEXY = ["","Maennchen", "Weibchen", "Totfund/ Koerperteile", "immatur"]

# ------------------------------------------------------------------------------------------------------------
# 2.7 Empty button
#
# In case you want to empty all entry fields
# ------------------------------------------------------------------------------------------------------------

def clear_everything():
    """Setzt wirklich alle Felder komplett auf leer, unabhängig von keep_all etc."""
    for f in FUNDORT_FIELDS + BEOB_FIELDS + [art_entry, nadel, sex, proof]:
        if isinstance(f, ttk.Combobox):
            f.current(0)
        else:
            f.delete(0, tk.END)
    listbox.delete(0, tk.END)

    # empty previews
    art_preview.config(text="")
    fund_preview.config(text="")
    nadel_preview.config(text="")
    nadel_extra.config(text="")

    # status update
    status.config(text="✖ Alle Felder geleert")


# ------------------------------------------------------------------------------------------------------------
# 2.8 Help functions for data entry fields
# ------------------------------------------------------------------------------------------------------------

def fe(parent, label, row, col, width=18, bold=False, fontsize=None):
    
    font = None
    
    if bold or fontsize:
        size = fontsize if fontsize else 10
        weight = "bold" if bold else "normal"
        font = tkFont.Font(size=size, weight=weight)

    ttk.Label(parent, text=label, font=font).grid(
        row=row, column=col*2, sticky="e", padx=5, pady=3
    )

    entry = ttk.Entry(parent, width=width)
    entry.grid(row=row, column=col*2+1, sticky="w", padx=5, pady=3)

    return entry
    
# ------------------------------------------------------------------------------------------------------------
# 2.9 Creating three preview windows in top and two ones next to the entry field
# ------------------------------------------------------------------------------------------------------------

def sex_symbol(value): # use pretty symbols for preview instead of text
    return {"Maennchen": "♂", "Weibchen": "♀", "Totfund/ Koerperteile": "†", "immatur": "🐛"}.get(value, "")

def update_preview(event=None):

    # Species
    art_preview.config(
        text=f"{sex_symbol(sex.get())} {art_entry.get()}\n"
             f"det. {det.get()}" 
    )
    # Location
    fund_preview.config(
        text=f"{country.get()} {region.get()} {village.get()}\n"
             f"{method.get()} {comment.get()}\n"
             f"{lat.get()} °N, {lng.get()} °E\n"
             f"{date1.get()} - {date2.get()} {height.get()} m ü. NN\n"
             f"leg. {leg.get()}"
    )

    # last Nadel
    nadel_preview.config(
        text=f"{nadel.get()} \n"
             f"± {precision.get()} m\n"
             f"{location.get()} \n"
             f"{habitat.get()} \n"
             f"{pcomment.get()} {project.get()}"
    )
    
    # last Nadel with p
    last = last_nadel()
    last_p = last_nadel_with_p()
    nadel_extra.config(
        text=f"Letzte: {last} | {last_p}"
    )

# ------------------------------------------------------------------------------------------------------------
# 2. Arrangement of preview and entry field containers
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# 2.1 Species selection (left)
# ------------------------------------------------------------------------------------------------------------

frame_art = ttk.LabelFrame(root, text="Art")
frame_art.pack(fill="x", padx=20, pady=5)

art_container = ttk.Frame(frame_art)
art_container.pack(fill="x",padx=100, pady=5)

entry_list_container = ttk.Frame(art_container)
entry_list_container.pack(side="left", padx=(0,20))

art_entry = ttk.Entry(entry_list_container, width=40)
art_entry.pack(pady=(0,5))
art_entry.bind("<KeyRelease>", on_keyrelease, add="+")

listbox = tk.Listbox(entry_list_container, height=5, width=40)
listbox.pack()
listbox.bind("<<ListboxSelect>>", on_listbox_select)

# ------------------------------------------------------------------------------------------------------------
# 2.2 Checkboxes and preview container (right)
# ------------------------------------------------------------------------------------------------------------

right_container = ttk.Frame(art_container)
right_container.pack(side="left", fill="x")

# Container 1: checkboxes and empty button

checkbox_container = ttk.Frame(right_container)
checkbox_container.pack(side="left", padx=5, anchor="w")

keep_fundort = tk.BooleanVar(value=False)
keep_beob = tk.BooleanVar(value=False)
keep_all = tk.BooleanVar(value=False)

ttk.Checkbutton(checkbox_container, text="Fundort übernehmen", variable=keep_fundort).pack(anchor="w")
ttk.Checkbutton(checkbox_container, text="Beobachtung übernehmen", variable=keep_beob).pack(anchor="w")
ttk.Checkbutton(checkbox_container, text="Alles übernehmen", variable=keep_all).pack(anchor="w")
ttk.Button(checkbox_container, text="Alles leeren", command=clear_everything).pack(anchor="w", pady=(5,0))

# Container 2: species preview

preview_font = tkFont.Font(size=14)

preview_sp_container = ttk.Frame(right_container)
preview_sp_container.pack(side="left", padx=10)

art_preview_frame = ttk.LabelFrame(preview_sp_container)
art_preview_frame.pack(side="top", pady=5)
art_preview = ttk.Label(art_preview_frame, justify="left", width=40, font = preview_font)
art_preview.pack(padx=5, pady=5)

# Container 3: first location and observation preview

preview_ort_container = ttk.Frame(right_container)
preview_ort_container.pack(side="left", padx=10, fill="x")

fund_preview_frame = ttk.LabelFrame(preview_ort_container)
fund_preview_frame.pack(side="top", pady=5)
fund_preview = ttk.Label(fund_preview_frame, justify="left", width=30, font = preview_font)
fund_preview.pack(padx=5, pady=5)

# Container 4: second location and observation preview

preview_u_container = ttk.Frame(art_container)
preview_u_container.pack(side="left", fill="x")

nadel_preview_frame = ttk.LabelFrame(preview_u_container)
nadel_preview_frame.pack(side="top", pady=5, fill="x")
nadel_preview = ttk.Label(nadel_preview_frame, width=30, font = preview_font, anchor="e", justify="right")
nadel_preview.pack(padx=5, pady=5, fill="x")

# ------------------------------------------------------------------------------------------------------------
# 2.3 Field for location
# ------------------------------------------------------------------------------------------------------------

fundort_frame = ttk.LabelFrame(root, text="Fundort")
fundort_frame.pack(fill="x", padx=10, pady=0)

country     = fe(fundort_frame, "country",  0, 0, width=3)
region      = fe(fundort_frame, "region",   0, 1, width=3)
village     = fe(fundort_frame, "village",  0, 2, width=20)
location    = fe(fundort_frame, "location", 0, 3, width=50)
habitat     = fe(fundort_frame, "habitat",  0, 4, width=30)

lat         = fe(fundort_frame, "lat",      0, 5, width=8)
lng         = fe(fundort_frame, "lng",      0, 6, width=8)
height      = fe(fundort_frame, "height",   0, 7, width=4)
precision   = fe(fundort_frame, "precision",0, 8, width=4)

# ------------------------------------------------------------------------------------------------------------
# 2.4 Fields for observations
# 
# Fields are arranged in a way, you can quickly enter data with tab.
# ------------------------------------------------------------------------------------------------------------


beob_frame = ttk.LabelFrame(root, text="Beobachtung")
beob_frame.pack(fill="x", padx=10, pady=5)

# left side: information used often
beob_left = ttk.Frame(beob_frame)
beob_left.grid(row=0, column=0, sticky="nw", padx=(10,20))

# seperator line
separator = ttk.Separator(beob_frame, orient="vertical")
separator.grid(row=0, column=1, sticky="ns")

# right side: rarely used fields
beob_right = ttk.Frame(beob_frame)
beob_right.grid(row=0, column=2, sticky="nw", padx=(20,10))

sex = fc(beob_left, "sex", 0, 0, values=SEXY, width=16)
comment = fe(beob_left, "comment", 0, 1, width=20)
pcomment = fe(beob_left, "pcomment", 0, 2, width=20)
date1  = fe(beob_left, "date1",    0, 3, width=9)
date2  = fe(beob_left, "date2",    0, 4, width=9)
proof   = fe(beob_left, "proof",   0, 5, width=2, bold=True, fontsize=12)
count  = fe(beob_left, "count",    0, 6, width=3, bold=True, fontsize=12)
leg     = fe(beob_left, "leg",     1, 0, width=20)
det     = fe(beob_left, "det",     1, 1, width=20)
vid     = fe(beob_left, "vid",     1, 2, width=20)
coll    = fe(beob_left, "coll",    1, 3, width=20)
method = fc(beob_left, "method", 1, 4, values=METHODEN, width=16)
nadel   = fe(beob_left, "Nadel",   1, 5, width=5, bold=True, fontsize=12)
nadel_extra = ttk.Label(beob_left, width=17, justify="left", anchor="w")
nadel_extra.grid(row=1, column=12, columnspan=7, sticky="we", padx=5, pady=3)

abg     = fe(beob_right, "abg",     0, 0, width=1)
old     = fe(beob_right, "old",     0, 1, width=1)
pic     = fe(beob_right, "pic",     0, 2, width=1)
eppi    = fe(beob_right, "eppi",     0, 3, width=5)
loan    = fe(beob_right, "loan",    1, 0, width=1)
new     =fe(beob_right, "new",      1, 1, width=1)
ill     = fe(beob_right, "ill",     1, 2, width=1)
project   = fe(beob_right, "project",1, 3, width=20)

FUNDORT_FIELDS = [country, region, village, location, habitat, lat, lng, height, precision]
BEOB_FIELDS = [comment, pcomment, date1, date2, method, count, leg, det, vid, coll, eppi, abg, old, project, loan, new, ill, pic]

# ------------------------------------------------------------------------------------------------------------
# 2.5 prefilling certain fields
# ------------------------------------------------------------------------------------------------------------

DEFAULT_PERSON = "Tristan Schirok"

for field in (leg, det, coll):
    field.insert(0, DEFAULT_PERSON)
    
WATCH_FIELDS = [
    art_entry, sex, det,
    country, region, village,
    method, comment,
    lat, lng, date1, date2, height,
    leg, nadel, precision, location, habitat,
    pcomment, project,loan, new, ill, pic
]

for field in WATCH_FIELDS:
    try:
        field.bind("<KeyRelease>", update_preview, add="+")
    except:
        field.bind("<<ComboboxSelected>>", update_preview, add="+")

# ------------------------------------------------------------------------------------------------------------
# 2.6 Save and refresh Button
# ------------------------------------------------------------------------------------------------------------
# Save-Button:
ttk.Button(root, text="💾 Speichern", command=save_entry).pack(pady=5)
status = tk.Label(root, text="")
status.pack()

# Refresh-Button:
table_container = ttk.Frame(root)
table_container.pack(fill="both", expand=True, padx=10, pady=5)

ttk.Button(
    table_container,
    text="🔄 Refresh",
    command=refresh_table
).pack(anchor="e", pady=2)

frame_table = ttk.Frame(table_container)
frame_table.pack(fill="both", expand=True)

# ------------------------------------------------------------------------------------------------------------
# 2.7 Creating preview table
# ------------------------------------------------------------------------------------------------------------

columns = ("ID", "Nadel", "spname", "sex", "country","region", "village", "location", "habitat", "comment", "pcomment", "date1", "date2",  "method", "count", "lat", "lng", "precision", "height", "leg", "det", "vid", "coll","proof","abg", "loan", "project","eppi", "old", "ill", "new","pic")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")

# Adding scrollbars
scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

# Columns:
for col in columns:
    tree.heading(col, text=col)
    tree.column("ID",       width=60,  anchor="center", stretch=False)
    tree.column("Nadel",    width=60,  anchor="center", stretch=False)
    tree.column("spname",   width=260, anchor="center", stretch=False)
    tree.column("sex",   width=60, anchor="center", stretch=False)    
    tree.column("country",  width=40,  anchor="center", stretch=False)
    tree.column("region",   width=40,  anchor="center", stretch=False)
    tree.column("village",  width=150, anchor="center", stretch=False)
    tree.column("location", width=200, anchor="center", stretch=False)
    tree.column("habitat",  width=180, anchor="center", stretch=False)
    tree.column("comment",  width=200, anchor="center", stretch=False)
    tree.column("pcomment",  width=200, anchor="center", stretch=False)
    tree.column("date1",    width=80, anchor="center", stretch=False)
    tree.column("date2",    width=80, anchor="center", stretch=False)
    tree.column("method",   width=100, anchor="center", stretch=False)
    tree.column("count",    width=40,  anchor="center", stretch=False)
    tree.column("lat",      width=75, anchor="center", stretch=False)
    tree.column("lng",      width=75, anchor="center", stretch=False)
    tree.column("precision", width=60, anchor="center", stretch=False)
    tree.column("height",   width=60, anchor="center", stretch=False)
    tree.column("leg",      width=110, anchor="center", stretch=False)
    tree.column("det",      width=110, anchor="center", stretch=False)
    tree.column("vid",      width=110, anchor="center", stretch=False)
    tree.column("coll",     width=110, anchor="center", stretch=False)
    tree.column("proof",    width=40, anchor="center", stretch=False)
    tree.column("abg",      width=40, anchor="center", stretch=False)
    tree.column("loan",     width=40, anchor="center", stretch=False)
    tree.column("project",  width=110, anchor="center", stretch=False)
    tree.column("eppi",     width=40, anchor="center", stretch=False)
    tree.column("old",      width=40, anchor="center", stretch=False)
    tree.column("ill",      width=40, anchor="center", stretch=False)
    tree.column("new",      width=40, anchor="center", stretch=False)
    tree.column("pic",      width=40, anchor="center", stretch=False)

# ------------------------------------------------------------------------------------------------------------
# 2.8 Data selection from table
#
# This one has to be nested within the table code. 
# ------------------------------------------------------------------------------------------------------------

tree.grid(row=0, column=0, sticky="nsew")

def on_tree_select(event):
    if not tree.selection():
        return
    
    # Selected row
    item_id = tree.selection()[0]
    values = tree.item(item_id, "values")

    # Mapping of colums to entry fields
    field_map = {
        "sex": sex,
        "country": country,
        "region": region,
        "village": village,
        "location": location,
        "habitat": habitat,
        "comment": comment,
        "pcomment": pcomment,
        "date1": date1,
        "date2": date2,
        "method": method,
        "count": count,
        "lat": lat,
        "lng": lng,
        "precision": precision,
        "height": height,
        "leg": leg,
        "det": det,
        "vid": vid,
        "coll": coll,
        "proof": proof,
        "abg": abg,
        "loan": loan,
        "project": project,
        "eppi": eppi,
        "old": old,
        "ill": ill,
        "new": new,
        "pic": pic,
        "Nadel": nadel
    }

    for col, field in field_map.items():
        if col in columns:
            idx = columns.index(col)
            value = values[idx]
            if isinstance(field, ttk.Combobox):
                try:
                    field.set(value)
                except:
                    field.current(0)
            else:
                field.delete(0, tk.END)
                field.insert(0, value)

    # update preview
    update_preview()


tree.bind("<<TreeviewSelect>>", on_tree_select)
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_table.rowconfigure(0, weight=1)
frame_table.columnconfigure(0, weight=1)


# ------------------------------------------------------------------------------------------------------------
# 3 Clear fields
#
# When entering some fields should be cleared, some not in certain cases. 
# ------------------------------------------------------------------------------------------------------------

def clear_fields():
    # Fields that should always be cleared to avaid mistakes:
    clear_combobox(sex)
    proof.delete(0,tk.END)
    nadel.delete(0,tk.END)    
    art_entry.delete(0, tk.END)
    listbox.delete(0, tk.END)

    # Cases if Checkboxes are selected -> do not clear certain fields:
    if keep_all.get():
        return

    if not keep_fundort.get():
        for f in FUNDORT_FIELDS:
            f.delete(0, tk.END)

    if not keep_beob.get():
        for f in BEOB_FIELDS:
            if isinstance(f, ttk.Combobox):
                clear_combobox(f)
            else:
                f.delete(0, tk.END)

        for field in (leg, det, vid, coll):
            field.insert(0, DEFAULT_PERSON)

def clear_combobox(cb):
    cb.current(0) 


# =================================================
# START
# =================================================
show_last()
root.mainloop()

