-- Ten plik zawiera zapytania SQLite do dodania brakujących kolumn
ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny';
ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0;
ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0;
