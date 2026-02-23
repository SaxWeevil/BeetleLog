import sqlite3

# connect to the SQL database
conn = sqlite3.connect('arten.db', check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL;")
c = conn.cursor()

# ------------------------------------------------------------------------------------------------------------
# 0. Introduction
#
# Attention! This database was made for German users. Thus, some terms in this code may be confusing for you!
# Please pay close attention about terms like "Art" and "Arten" (= species).
#
# The SQL database consists of three tables:
# 
# 1. Arten = species data: contains taxonomic information like genus, species, author, year. In my case, I
#            wanted to use only my used taxon names. In this way, I'm always aware, if a species is new to my
#            collection
# 2. Beobachtung = observation data: contains information like date, method, comments and foreign keys for
#                  the "Arten" and "Fundort" table.
# 3. Fundort = location data: contains information like country, region, location, coordinates, precision and
#              height.
#
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# 1. Functions
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# 1.1 Autocompletion and creation in species selection
#
# - add_art: adds a new species (= Art) to the species table in this way: genus + space + species
#   - enter "Ceutorhynchus pallidactylus" stores genus: Ceutorhynchus and species: pallidactylus
#   - enter "Ceutorhynchus pallidactylus (Marsham, 1802)" stores genus: Ceutorhynchus
#           and species: pallidactylus (Marsham, 1802)
#   - so all information behind the first space will be stored in the species section. It does not recognize 
#     the author, parenthesis or year information. Why? Because there are many ways to enter typos and trick a
#     algorithm by accident. I think it's more secure to add this information later in a database program like
#     DB Browser manually.
#   - you always have to enter a species name. Genus alone is not allowed. If you enter a undetermined species
#     go for: Ceutorhynchus sp. for example. This creates a new species of Ceutorhynchus sp.    
#
# - autocomplete_art and get_art_by_name: automatically finds the species name if exists that you want to enter
#
# ------------------------------------------------------------------------------------------------------------
def add_art(fhlcode, familia, subfamilia, genus, species, parenthesis, author, year):
    c.execute('''
        INSERT INTO Arten
        (fhlcode, familia, subfamilia, genus, species, parenthesis, author, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fhlcode, familia, subfamilia, genus, species, parenthesis, author, year))
    conn.commit()
    return c.lastrowid

def autocomplete_art(teil_name):
    c.execute("""
        SELECT Art_ID, spname
        FROM Arten_mit_Name
        WHERE spname LIKE ?
    """, ('%' + teil_name + '%',))
    return c.fetchall()
    
def get_art_by_name(genus, species):
    c.execute("SELECT Art_ID FROM Arten WHERE genus=? AND species=?", (genus, species))
    result = c.fetchone()
    return result[0] if result else None
    

# ------------------------------------------------------------------------------------------------------------
# 1.2 Location functions
# 
# - find_fundort and get_or_create_fundort: before adding a new location ID this algorithms check stored
#   information and try to find the exact same. If it recognized an already used location it uses the same ID.
#   If only one letter is different anywhere it creates a new location.
#
# - ChatGPT advice: use IS NOT DISTINCT FROM ? instead of IS ?
#
# ------------------------------------------------------------------------------------------------------------
def find_fundort(country, region, village, location, habitat,
                 lat, lng, height, precision):
    c.execute("""
        SELECT Fundort_ID
        FROM Fundort
        WHERE
            country   IS ?
        AND region    IS ?
        AND village   IS ?
        AND location  IS ?
        AND habitat   IS ?
        AND lat       IS ?
        AND lng       IS ?
        AND height    IS ?
        AND precision IS ?
    """, (country, region, village, location, habitat,
          lat, lng, height, precision))
    row = c.fetchone()
    return row[0] if row else None


def get_or_create_fundort(country, region, village, location, habitat,
                          lat, lng, height, precision):

    fundort_id = find_fundort(
        country, region, village, location, habitat,
        lat, lng, height, precision
    )

    if fundort_id is not None:
        return fundort_id  # already exists

    # or create a new one
    c.execute("""
        INSERT INTO Fundort
        (country, region, village, location, habitat,
         lat, lng, height, precision)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (country, region, village, location, habitat,
          lat, lng, height, precision))
    conn.commit()
    return c.lastrowid

# ------------------------------------------------------------------------------------------------------------
# 1.3 Observation functions
#
# - add_beobachtung: adds a new observation
#
# - last_beobachtungen: selects the last 500 observations created and stores them in this container. This
#   information is later used to create the table preview.
#   
# ------------------------------------------------------------------------------------------------------------
def add_beobachtung(count, date1, date2, method, proof, comment, pcomment, leg, det, vid, coll, fundort_id, art_id, nadel, abg, loan, project, eppi, old, ill, new, sex, pic):
    c.execute('''INSERT INTO Beobachtung
                 (count, date1, date2, method, proof, comment, pcomment, leg, det, vid, coll, Fundort_ID, Art_ID, Nadel, abg, loan, project, eppi, old, ill, new, sex, pic)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (count, date1, date2, method, proof, comment, pcomment, leg, det, vid, coll, fundort_id, art_id, nadel, abg, loan, project, eppi, old, ill, new, sex, pic))
    conn.commit()
    return c.lastrowid

def last_beobachtungen():
    c.execute('''
        SELECT
            Beobachtung.Beobachtung_ID,
            Beobachtung.Nadel,
            art.spname,
            Beobachtung.sex,
            Fundort.country,
            Fundort.region,
            Fundort.village,
            Fundort.location,
            Fundort.habitat,
            Beobachtung.comment,
            Beobachtung.pcomment,
            Beobachtung.date1,
            Beobachtung.date2,
            Beobachtung.method,
            Beobachtung.count,
            Fundort.lat,
            Fundort.lng,
            Fundort.precision,
            Fundort.height,
            Beobachtung.leg,
            Beobachtung.det,
            Beobachtung.vid,
            Beobachtung.coll,
            Beobachtung.proof,
            Beobachtung.abg,
            Beobachtung.loan,
            Beobachtung.project,
            Beobachtung.eppi,
            Beobachtung.old,
            Beobachtung.ill,
            Beobachtung.new,
            Beobachtung.pic
        FROM Beobachtung
        JOIN Arten_mit_Name AS art
            ON Beobachtung.Art_ID = art.Art_ID
        JOIN Fundort
            ON Beobachtung.Fundort_ID = Fundort.Fundort_ID
        ORDER BY Beobachtung.Beobachtung_ID DESC
        LIMIT 500
    ''')
    return c.fetchall()
    
# ------------------------------------------------------------------------------------------------------------
# 1.4 Preview functions
#
# - last_nadel and last_nadel_with_p: select certain data to create a preview window in the frontend
#
#
# ------------------------------------------------------------------------------------------------------------
def last_nadel():
    """Gibt die letzte Nadel zurück"""
    c.execute('''
        SELECT Nadel
        FROM Beobachtung
        WHERE Nadel NOT LIKE '%P%'
        ORDER BY Beobachtung_ID DESC
        LIMIT 1
    ''')
    row = c.fetchone()
    return row[0] if row else ""

def last_nadel_with_p():
    """Gibt die letzte Nadel zurück, die ein 'P' enthält"""
    c.execute('''
        SELECT Nadel
        FROM Beobachtung
        WHERE Nadel LIKE '%P%'
        ORDER BY Beobachtung_ID DESC
        LIMIT 1
    ''')
    row = c.fetchone()
    return row[0] if row else ""


# ------------------------------------------------------------------------------------------------------------
# 2. Tables and Views
#
# - creates the tables Arten, Beobachtung and Fundort as well as a unique index for security reasons
# 
# - creates also a VIEW Arten_mit_Name which is used for species autocompletion
#
#
# ------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    c.execute('''CREATE TABLE IF NOT EXISTS Arten (
        Art_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        fhlcode TEXT,
        familia TEXT,
        subfamilia TEXT,
        genus TEXT,
        species TEXT,
        parenthesis INTEGER,
        author TEXT,
        year INTEGER,
        UNIQUE(genus, species)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS Fundort (
        Fundort_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT,
        region TEXT,
        village TEXT,
        location TEXT,
        habitat TEXT,
        lat REAL,
        lng REAL,
        height REAL,
        precision INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS Beobachtung (
        Beobachtung_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        count INTEGER,
        date1 DATE,
        date2 DATE,
        method TEXT,
        proof TEXT,
        comment TEXT,
        pcomment TEXT,
        leg TEXT,
        det TEXT,
        vid TEXT,
        coll TEXT,
        Fundort_ID INTEGER,
        Art_ID INTEGER,
        Nadel TEXT,
        abg TEXT,
        loan TEXT,
        project TEXT,
        eppi TEXT,
        old TEXT,
        ill TEXT,
        new TEXT,
        sex TEXT,
        pic TEXT,
        FOREIGN KEY(Fundort_ID) REFERENCES Fundort(Fundort_ID),
        FOREIGN KEY(Art_ID) REFERENCES Arten(Art_ID)
    )''')

    # Arten mit Name
    c.execute('''
        CREATE VIEW IF NOT EXISTS Arten_mit_Name AS
        SELECT
            Art_ID,
            genus || ' ' || species ||
            CASE 
                WHEN parenthesis = '' THEN ''  -- leer, wenn keine Angabe
                WHEN parenthesis <> 0 THEN ' (' || author || ', ' || year || ')'
                ELSE ' ' || author || ', ' || year
            END AS spname
        FROM Arten;
        
    ''')
    
    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_fundort_unique
        ON Fundort (
            country, region, village, location, habitat,
            lat, lng, height, precision
        )
    ''')

    conn.commit()
    print("Datenbank und Tabellen erstellt!")

