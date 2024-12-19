--таблица Genres
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,  --уникальный идентификатор жанра
    name VARCHAR(50) NOT NULL UNIQUE --название жанра, уникальное
);

--таблица Artists
CREATE TABLE artists (
    artist_id SERIAL PRIMARY KEY,  --уникальный идентификатор артиста
    name VARCHAR(100) NOT NULL,    --имя артиста
    country VARCHAR(50),           --страна
    genre_id INT NOT NULL,         --ссылка на жанр
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id) --связь с таблицей genres
);

--таблица Albums
CREATE TABLE albums (
    album_id SERIAL PRIMARY KEY,   --уникальный идентификатор альбома
    title VARCHAR(100) NOT NULL,   --название альбома
    artist_id INT NOT NULL,        --ссылка на артиста
    genre_id INT NOT NULL,          --ссылка на жанр
    release_date DATE,             --дата выхода альбома
    sales INT,                     --продажи
    FOREIGN KEY (artist_id) REFERENCES artists (artist_id), --связь с таблицей artists
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id)   --связь с таблицей genres
);

--таблица Reviews
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,        --уникальный идентификатор отзыва
    album_id INT NOT NULL,               --ссылка на альбом
    user_id INT NOT NULL,                --ссылка на пользователя, который оставил отзыв
    rating INT CHECK (rating BETWEEN 1 AND 10), --рейтинг от 1 до 10
    review_text TEXT,                    --текст отзыва
    created_at TIMESTAMP DEFAULT NOW(),  --дата создания отзыва
    FOREIGN KEY (album_id) REFERENCES albums (album_id), --связь с таблицей albums
    FOREIGN KEY (user_id) REFERENCES users (user_id)     --связь с таблицей users
);


--таблица Awards
CREATE TABLE awards (
    award_id SERIAL PRIMARY KEY,   --уникальный идентификатор награды
    album_id INT NOT NULL,         --ссылка на альбом
    award_name VARCHAR(100) NOT NULL, --название награды
    award_year INT,                --год получения награды
    FOREIGN KEY (album_id) REFERENCES albums (album_id) --связь с таблицей albums
);

--таблица Metrics
CREATE TABLE metrics (
    metric_id SERIAL PRIMARY KEY,  --уникальный идентификатор метрики
    album_id INT NOT NULL,         --ссылка на альбом
    streams INT,                   --количество стримов
    downloads INT,                 --количество скачиваний
    FOREIGN KEY (album_id) REFERENCES albums (album_id) --связь с таблицей albums
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,          --уникальный идентификатор пользователя
    username VARCHAR(50) NOT NULL UNIQUE, --уникальное имя пользователя
    email VARCHAR(100) NOT NULL UNIQUE, --уникальный адрес электронной почты
    password_hash VARCHAR(255) NOT NULL, --хэш пароля
    role VARCHAR(20) DEFAULT 'user',    --роль пользователя (например, 'user', 'admin')
    created_at TIMESTAMP DEFAULT NOW()  --дата создания пользователя
);
