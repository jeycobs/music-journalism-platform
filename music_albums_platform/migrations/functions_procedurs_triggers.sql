--создание представлений
CREATE OR REPLACE VIEW genre_popularity AS
SELECT 
    g.name AS genre, 
    SUM(a.sales) AS total_sales, 
    SUM(m.streams) AS total_streams
FROM genres g
JOIN albums a ON g.genre_id = a.genre_id
JOIN metrics m ON a.album_id = m.album_id
GROUP BY g.name
ORDER BY total_sales DESC;

--создание триггера для увеличения скачиваний
CREATE OR REPLACE FUNCTION increment_downloads()
RETURNS TRIGGER AS $$
BEGIN
    NEW.downloads = NEW.downloads + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increase_downloads_trigger
BEFORE UPDATE ON metrics
FOR EACH ROW
WHEN (NEW.downloads > OLD.downloads)
EXECUTE FUNCTION increment_downloads();

--функция для подсчета общего дохода
CREATE OR REPLACE FUNCTION calculate_album_revenue(album_id INT)
RETURNS NUMERIC AS $$
DECLARE
    album_revenue NUMERIC;
BEGIN
    SELECT 
        a.sales + (m.streams * 0.005)
    INTO album_revenue
    FROM albums a
    JOIN metrics m ON a.album_id = m.album_id
    WHERE a.album_id = album_id;

    RETURN album_revenue;
END;
$$ LANGUAGE plpgsql;

--хранимая процедура для добавления альбома
CREATE OR REPLACE PROCEDURE add_album_with_details(
    album_title TEXT, 
    artist_id INT, 
    genre_id INT, 
    release_date DATE, 
    sales INT, 
    award_name TEXT, 
    award_year INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_album_id INT;
BEGIN
    INSERT INTO albums (title, artist_id, genre_id, release_date, sales)
    VALUES (album_title, artist_id, genre_id, release_date, sales)
    RETURNING album_id INTO new_album_id;

    INSERT INTO awards (album_id, award_name, award_year)
    VALUES (new_album_id, award_name, award_year);

    INSERT INTO metrics (album_id, streams, downloads)
    VALUES (new_album_id, 0, 0);
END;
$$;
