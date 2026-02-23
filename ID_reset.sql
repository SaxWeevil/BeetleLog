UPDATE sqlite_sequence
SET seq = (SELECT MAX(Art_ID) FROM Arten)
WHERE name = 'Arten';