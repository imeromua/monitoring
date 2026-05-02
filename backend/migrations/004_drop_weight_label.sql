-- Міграція 004: видалення weight_label, зміна типу article_id
-- Виконати: psql -h localhost -U storecheck -d monitoring -f 004_drop_weight_label.sql

BEGIN;

-- 1. Видаляємо weight_label
ALTER TABLE products DROP COLUMN IF EXISTS weight_label;

-- 2. Змінюємо тип article_id на VARCHAR(8)
ALTER TABLE products ALTER COLUMN article_id TYPE VARCHAR(8);

-- 3. Перевіряємо що усі існуючі артикули відповідають формату (8 цифр)
-- (запис відкотиться якщо є невідповідні дані)
DO $$
DECLARE
    bad_count INT;
BEGIN
    SELECT COUNT(*) INTO bad_count
    FROM products
    WHERE article_id !~ '^\d{8}$';

    IF bad_count > 0 THEN
        RAISE NOTICE 'Увага: % артикулів не відповідають формату 8 цифр', bad_count;
    ELSE
        RAISE NOTICE 'OK: усі article_id відповідають формату';
    END IF;
END
$$;

COMMIT;
