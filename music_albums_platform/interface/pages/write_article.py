import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "musicdb",
    "user": "admin",
    "password": "test",
    "host": "localhost",
    "port": "5432",
}

def add_album_cover(album_id, image_file):
    try:
        #преобразование загруженного файла в байты
        image_data = image_file.read()
        
        #подключение к базе данных
        with psycopg2.connect(
            **DB_CONFIG
        ) as conn:
            with conn.cursor() as cursor:
                #обновление записи альбома с добавлением обложки
                cursor.execute(
                    """
                    UPDATE albums
                    SET cover_image = %s
                    WHERE album_id = %s
                    """,
                    (psycopg2.Binary(image_data), album_id)
                )
                conn.commit()
        st.success("Обложка альбома успешно добавлена!")
    except Exception as e:
        st.error(f"Ошибка при добавлении обложки: {e}")

def get_db_connection():
    """подключение к базе данных."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Ошибка подключения к базе данных: {e}")
        return None

def add_genre_if_not_exists(genre_name):
    """добавляет жанр, если он отсутствует в базе данных."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT genre_id FROM genres WHERE name = %s", (genre_name,))
                genre = cur.fetchone()
                if not genre:
                    cur.execute("INSERT INTO genres (name) VALUES (%s) RETURNING genre_id", (genre_name,))
                    conn.commit()
                    genre = cur.fetchone()
                return genre[0]
        except Exception as e:
            st.error(f"Ошибка добавления жанра: {e}")
        finally:
            conn.close()

def add_artist_if_not_exists(artist_name, country, genre_id):
    """добавляет артиста, если он отсутствует в базе данных."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT artist_id FROM artists WHERE name = %s", (artist_name,))
                artist = cur.fetchone()
                if not artist:
                    cur.execute(
                        "INSERT INTO artists (name, country, genre_id) VALUES (%s, %s, %s) RETURNING artist_id",
                        (artist_name, country, genre_id)
                    )
                    conn.commit()
                    artist = cur.fetchone()
                return artist[0]
        except Exception as e:
            st.error(f"Ошибка добавления артиста: {e}")
        finally:
            conn.close()
def get_albums():
    """получает список альбомов из базы данных."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT album_id, title FROM albums")
                return cur.fetchall()
        except Exception as e:
            st.error(f"Ошибка загрузки альбомов: {e}")
        finally:
            conn.close()
    return []

def add_album(title, artist_id, genre_id, release_date, sales, awards,awards_year,streams, downloads):
    """добавляет альбом в базу данных."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO albums (title, artist_id, genre_id, release_date, sales)
                    VALUES (%s, %s, %s, %s, %s) RETURNING album_id
                    """,
                    (title, artist_id, genre_id, release_date, sales)
                )
                album_id = cur.fetchone()[0]   
                #добавляем записи в таблицу Awards
                cur.execute(
                    """INSERT INTO awards (album_id, award_name, award_year)
                       VALUES (%s,%s,%s)
                    """,
                    (album_id, awards, awards_year)
                )

                #добавлкемк записи в таблицу Metrics
                cur.execute(
                    """INSERT INTO metrics(album_id, streams, downloads)
                       VALUES(%s, %s, %s)
                    """,
                    (album_id, streams, downloads)
                )
                conn.commit()
                #album = cur.fetchone()
                st.success(f"Альбом '{title}' успешно добавлен!")
                #return album[0]
        except Exception as e:
            st.error(f"Ошибка добавления альбома: {e}")
        finally:
            conn.close()

def add_review_to_db(user_id, album_id, rating, review_text):
    """добавляет отзыв в таблицу reviews."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO reviews (user_id, album_id, rating, review_text)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, album_id, rating, review_text)
                )
                conn.commit()
                st.success("Отзыв успешно добавлен!")
        except Exception as e:
            st.error(f"Ошибка добавления отзыва: {e}")
        finally:
            conn.close()

def adding_album_to_db():
    st.title("Добавление нового альбома")

    if 'authenticated' in st.session_state and st.session_state['authenticated']:
        with st.form("add_album_form"):
            album_title = st.text_input("Название альбома")
            artist_name = st.text_input("Имя артиста")
            artist_country = st.text_input("Страна артиста", value="Неизвестно")
            genre_name = st.text_input("Жанр")
            release_date = st.date_input("Дата выхода альбома")
            sales = st.number_input("Продажи (в единицах)", min_value=0, step=1)
            awards = st.text_input("Награды", value="Нет наград")
            awards_year = st.number_input("Год награды", min_value=0, step=1)
            streams = st.number_input("Стриминговая оценка", min_value=0, step=1)
            downloads = st.number_input("Количество скачиваний", min_value=0, step=1)
            image_file = st.file_uploader("Загрузить обложку альбома", type=["jpg", "jpeg", "png"])
        
            submit = st.form_submit_button("Добавить альбом")
        
            if submit:
                if not album_title or not artist_name or not genre_name:
                    st.error("Все поля должны быть заполнены!")
                else:
                    try:
                        genre_id = add_genre_if_not_exists(genre_name)
                        artist_id = add_artist_if_not_exists(artist_name, artist_country, genre_id)
                        album_id = add_album(album_title, artist_id, genre_id, release_date, sales, awards,awards_year, streams, downloads)
                    
                        if image_file and album_id:
                            add_album_cover(album_id, image_file)

                    except Exception as e:
                        st.error(f"Ошибка: {e}")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите на вкладке авторизации.")



def review_page():
    """интерфейс добавления отзыва."""
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.warning("Вы должны быть авторизованы для добавления отзыва.")
        st.session_state.update({"rerun": True}) 

    #st.header("Добавить отзыв")

    #получение списка альбомов
    album_list = get_albums()
    if not album_list:
        st.error("Нет доступных альбомов для выбора.")
        return

    album_options = {album['title']: album['album_id'] for album in album_list}
    #if st.button("Добавить альбом"):
    #    adding_album_to_db()
    #add_album_tab = st.tabs(["Добавить альбом"])
    #with add_album_tab[0]:
    adding_album_to_db()    #для добавления новых альбомов
    with st.form(key="review_form"):
        album_name = st.selectbox("Выберите альбом", options=list(album_options.keys()))
        rating = st.slider("Рейтинг", 1, 10, 5)
        review_text = st.text_area("Текст отзыва")

        submit_button = st.form_submit_button("Отправить")
        if submit_button:
            if not review_text.strip():
                st.error("Текст отзыва не может быть пустым.")
            else:
                add_review_to_db(
                    user_id=st.session_state.user_id,
                    album_id=album_options[album_name],
                    rating=rating,
                    review_text=review_text
                )