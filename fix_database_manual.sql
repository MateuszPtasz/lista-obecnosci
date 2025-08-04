-- SQL DO WYKONANIA RĘCZNEGO
--
-- Poniższe polecenia należy wykonać w narzędziu do obsługi bazy danych SQLite.
-- Dodadzą one brakujące kolumny do tabeli shifts.

-- 1. Dodanie kolumny 'status'
ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny';

-- 2. Dodanie kolumny 'is_holiday'
ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0;

-- 3. Dodanie kolumny 'is_sick'
ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0;

-- Po wykonaniu tych poleceń należy zweryfikować strukturę tabeli:
-- PRAGMA table_info(shifts);
