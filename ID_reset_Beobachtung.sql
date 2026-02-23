UPDATE sqlite_sequence
SET seq = (SELECT MAX(Beobachtung_ID) FROM Beobachtung)
WHERE name = 'Beobachtung';

UPDATE sqlite_sequence
SET seq = (SELECT MAX(Fundort_ID) FROM Fundort)
WHERE name = 'Fundort';