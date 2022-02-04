create table customer(
    id integer primary key,
    telegram_user_id integer unique,
    telegram_username text,
    telegram_full_name text
);
