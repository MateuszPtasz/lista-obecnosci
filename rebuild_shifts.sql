-- Skrypt SQL do przebudowy tabeli shifts z nowymi kolumnami

-- Najpierw tworzymy kopię tabeli shifts
CREATE TABLE shifts_backup AS SELECT * FROM shifts;

-- Zmień nazwę obecnej tabeli
ALTER TABLE shifts RENAME TO shifts_old;

-- Utwórz nową tabelę shifts ze wszystkimi potrzebnymi kolumnami
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT,
    start_time TIMESTAMP,
    stop_time TIMESTAMP,
    start_location TEXT,
    stop_location TEXT,
    start_latitude REAL,
    start_longitude REAL,
    stop_latitude REAL,
    stop_longitude REAL,
    duration_min INTEGER,
    status TEXT DEFAULT 'Obecny',
    is_holiday BOOLEAN DEFAULT 0,
    is_sick BOOLEAN DEFAULT 0
);

-- Przenieś dane ze starej tabeli do nowej
INSERT INTO shifts (
    id, employee_id, start_time, stop_time,
    start_location, stop_location,
    start_latitude, start_longitude, 
    stop_latitude, stop_longitude,
    duration_min
)
SELECT
    id, employee_id, start_time, stop_time,
    start_location, stop_location,
    start_latitude, start_longitude, 
    stop_latitude, stop_longitude,
    duration_min
FROM shifts_old;

-- Sprawdź liczbę rekordów w tabelach
SELECT 'shifts_old', COUNT(*) FROM shifts_old;
SELECT 'shifts', COUNT(*) FROM shifts;

-- Sprawdź strukturę nowej tabeli
PRAGMA table_info(shifts);
