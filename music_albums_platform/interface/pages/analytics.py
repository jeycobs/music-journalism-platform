import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

#настройки подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "musicdb",
    "user": "admin",
    "password": "test",
    "host": "localhost",
    "port": "5432", 
}

#устанавливаем соединение с базой данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            **DB_CONFIG
        )
        return conn
    except Exception as e:
        st.error(f"Ошибка соединения с базой данных: {e}")
        return None

#выполняем SQL-запрос и возвращаем результат в виде DataFrame
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                colnames = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=colnames)
        except Exception as e:
            st.error(f"Ошибка выполнения запроса: {e}")
        finally:
            conn.close()
def album_ratings_page():
    st.title("Рейтинги альбомов")

    query = """
    SELECT a.title AS album, ar.name AS artist, AVG(r.rating) AS avg_rating
    FROM albums a
    JOIN artists ar ON a.artist_id = ar.artist_id
    JOIN reviews r ON a.album_id = r.album_id
    GROUP BY a.title, ar.name
    ORDER BY avg_rating DESC;
    """
    df = execute_query(query)

    if not df.empty:
        st.subheader("Таблица рейтингов альбомов")
        st.dataframe(df)

        # график среднего рейтинга альбомов
        fig = px.bar(df, x="album", y="avg_rating", color="artist", title="Средние рейтинги альбомов", labels={"avg_rating": "Рейтинг"})
        st.plotly_chart(fig)
    else:
        st.warning("Нет данных для отображения.")

# страница: Связь стримов и скачиваний
def streams_vs_downloads_page():
    st.title("Связь стримов и скачиваний")

    query = """
    SELECT a.title AS album, m.streams, m.downloads
    FROM albums a
    JOIN metrics m ON a.album_id = m.album_id;
    """
    df = execute_query(query)

    if not df.empty:
        st.subheader("Таблица стримов и скачиваний")
        st.dataframe(df)

        #график связи
        fig = px.scatter(df, x="streams", y="downloads", text="album", title="Связь стримов и скачиваний", labels={"streams": "Стримы", "downloads": "Скачивания"})
        st.plotly_chart(fig)
    else:
        st.warning("Нет данных для отображения.")

#страница: Популярность жанров
def genre_popularity_page():
    st.title("Популярность жанров")

    query = """
    SELECT * FROM genre_popularity;
    """
    df = execute_query(query)

    if df is not None and not df.empty:
        st.subheader("Таблица популярности жанров")
        st.dataframe(df)

        #график по продажам
        fig_sales = px.bar(df, x="genre", y="total_sales", title="Продажи по жанрам", labels={"total_sales": "Продажи"})
        st.plotly_chart(fig_sales)

        #график по стримам
        fig_streams = px.bar(df, x="genre", y="total_streams", title="Стримы по жанрам", labels={"total_streams": "Стримы"})
        st.plotly_chart(fig_streams)
    else:
        st.warning("Нет данных для отображения.")



def analytics_page():
    st.title("Аналитика которую создаете Вы!")
    genre_popularity_page()
    album_ratings_page()
    streams_vs_downloads_page()
