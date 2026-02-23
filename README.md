# BeetleLog

This program creates a simple collection database using SQLite and a
Python-based frontend. It is designed to allow fast and efficient entry
of beetle specimen data into a structured database. The main purpose of
this tool is rapid data entry. It is not intended to provide full
database management functionality within the frontend itself.

My typical workflow using this program is:

1.  Prepare the specimens from fridge
2.  Enter location and observation data
3.  Determine the species
4.  Write labels and prepare the pin
5.  Save the observation to the database

Using SQLite has several advantages:

-   You can manage the database later using free external software
    (e.g., DB Browser for SQLite).
-   Data can easily be exported via SQL queries.
-   Export to formats such as .csv is straightforward.
-   You can create custom SQL Views in your database software to
    simplify data management and exports.

The program was primarily developed for German users. Some field names
and structures are designed to allow quick export of data to
coleoweb.de.

✔ Runs offline ✔ No server needed ✔ Uses a single SQLite database file ✔
Fully transparent structure

## Overview

![](pictures/Eingefügtes%20Bild.png)

The interface consists of:

-   Species selection with autocompletion
-   Three live preview panels
-   Location input fields
-   Observation input fields
-   Table preview of last 500 entries

🏗 Project Structure

The project consists of three files: database.py, frontend.py and
arten.db

The database is automatically created if not exists as: arten.db

The provided arten.db contains some test data to play around.

It contains three tables:

🐞 1. Arten (Species Table)

Stores species related information: genus, species, author, year, family
fields (optional)

Duplicate species are prevented using: UNIQUE(genus, species)

This ensures: No duplicate species names

📍 2. Fundort (Location Table)

Stores collecting site data: country, region, village, location
description, habitat, latitude, longitude, elevation, precision

A UNIQUE INDEX prevents identical locations: idx_fundort_unique

This means: If every single field matches exactly → the location will be
reused.

📝 3. Beobachtung (Observation Table)

This table connects: One species (Art_ID), One location (Fundort_ID) and
stores obersvation data such as: date, method, sex, collector (leg.),
determiner (det.)

Each entry represents a specimen record.

🔎 Species Autocompletion System

When typing a species: Existing names are suggested and new names are
created automatically if not found. You can type directly the species
name if it exists.

⚠ Important: You must enter a new species as: Genus species

Example: Ceutorhynchus pallidactylus

Do not type: Ceutorhynchus pallidactylus (Marsham, 1802) as this would
save genus = "Ceutorhynchus" and species = "pallidactylus (Marsham,
1802)"

The algorithm just recognizes the first space and group all information
behind this space in the species column. Why?

Because it's difficult to program a algorithm for all variants of author
names. Thus I decided to simply add a new species this way and edit it
later in DB Browser to ensure stability.

Genus alone is not allowed. If doing so, you will get a error message.

If you want to enter a undetermined species use dummy's for example:
Ceutorhynchus sp.

## Frontend Structure (frontend.py)

### 🐞 Species Section

![](pictures/Eingefügtes%20Bild%20(2).png)

Left side: Species entry field + Autocomplete suggestion list

Right side: Checkboxes for saving certain information after adding the
observation

Three preview windows (Live Preview System): I use them to write my
labels for the pin (I handwrite the labels)

### 📸 Location and Observation section

![](pictures/Eingefügtes%20Bild%20(3).png)

⚠ Important: The function get_or_create_fundort() ensures:

✔ Existing identical locations are reused ✔ Slight differences create a
new location ID

-   Tab navigation is optimized for fast data entry:
    -   Left side: Frequently used fields
    -   Right side: Rarely used fields

### 💾 Save Process

The program: checks species validity, creates species if not existing,
finds or creates locations, inserts observation, updates preview,
refreshes the table and clears selected fields (depending on checkboxes)

### 🔄 Refresh Button

Use this when: Editing the database externally (like with DB Browser)

⚠ Important: If you edit the database externally: You must SAVE in DB
Browser before returning.

Otherwise the frontend may freeze.

![](pictures/Bildschirmfoto%20vom%202026-02-23%2017-04-35.png)

### 📊 Table Preview

The lower table displays the last 500 observations.

Clicking a row: loads the data back into the entry fields and updates
preview automatically

Certain fields are not loaded to avoid mistakes (like counts, species
names, sex)

### Notes

Whenever you delete locations, species, or observations using an
external database tool, the ID counter does not reset automatically. If
you delete an observation and later add a new one, one ID number will be
skipped. This is normal behavior in SQLite and does not cause any
technical problems. However, if you prefer to maintain a continuous ID
sequence (for aesthetic or organizational reasons), you will need to
manually reset the ID counter after deleting records. For this purpose,
I have provided two .sql files that allow you to reset the ID sequence.
Please test these scripts carefully to ensure they meet your specific
requirements before using them in your production database.

## Enhancement

The provided version of the frontend is basic and not very visually
appealing at first. You can use ThemedTk and custom fonts to enhance the
interface quickly. If you’re unsure how to do this, simply copy the
frontend code into an AI tool like ChatGPT and ask for step-by-step
guidance on how to apply themes and fonts.

In Ubuntu I prefer to use the theme family "plastik" together with font
"Ubuntu".

## 🚀 Installation Requirements

1.  Python 3.9+
2.  tkinter (usually preinstalled)

How to run:

run in console: python database.py (creates the database in that folder
if not exists)

then run python frontend.py
