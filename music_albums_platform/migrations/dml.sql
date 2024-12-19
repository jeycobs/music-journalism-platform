--заполнение таблицы Genres
INSERT INTO genres (name) VALUES 
('Rock'),
('Pop'),
('Jazz'),
('Hip-Hop');

--заполнение таблицы Artists
INSERT INTO artists (name, country, genre_id) VALUES 
('The Beatles', 'United Kingdom', 1),
('Beyoncé', 'United States', 2),
('Miles Davis', 'United States', 3),
('Kendrick Lamar', 'United States', 4);

--заполнение таблицы Albums
INSERT INTO albums (title, artist_id, genre_id, release_date, sales) VALUES 
('Abbey Road', 1, 1, '1969-09-26', 10000000),
('Lemonade', 2, 2, '2016-04-23', 15000000),
('Kind of Blue', 3, 3, '1959-08-17', 5000000),
('Good Kid, M.A.A.D City', 4, 4, '2012-11-22', 7000000);

--заполнение таблицы Users
INSERT INTO users (username, email, password_hash, role) VALUES 
('john_doe', 'john@example.com', 'hashed_password_1', 'user'),
('admin', 'admin@example.com', 'hashed_password_2', 'admin'),
('jane_smith', 'jane@example.com', 'hashed_password_3', 'user');

--заполнение таблицы Reviews
INSERT INTO reviews (album_id, user_id, rating, review_text) VALUES 
(1, 1, 9, 'Amazing album! Timeless classic.'),
(2, 3, 8, 'Great production and vocals.'),
(3, 1, 10, 'A masterpiece in jazz history.'),
(4, 2, 7, 'Innovative and influential.');

--заполнение таблицы Awards
INSERT INTO awards (album_id, award_name, award_year) VALUES 
(1, 'Grammy Hall of Fame', 1995),
(2, 'Album of the Year', 2017),
(3, 'Grammy Hall of Fame', 2000),
(4, 'BBC Best Rap Album', 2012);

--заполнение таблицы Metrics
INSERT INTO metrics (album_id, streams, downloads) VALUES 
(1, 500000000, 2000000),
(2, 800000000, 3000000),
(3, 300000000, 1000000),
(4, 600000000, 2500000);
