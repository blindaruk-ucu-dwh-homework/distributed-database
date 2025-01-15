CREATE TABLE user_counter (
    USER_ID SERIAL PRIMARY KEY, -- Унікальний ідентифікатор користувача
    Counter INTEGER NOT NULL DEFAULT 0, -- Лічильник, за замовчуванням 0
    Version INTEGER NOT NULL DEFAULT 0 -- Версія, за замовчуванням 0
);
INSERT INTO user_counter (user_id, counter, version) VALUES (1, 0, 0);
