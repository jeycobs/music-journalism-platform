import streamlit as st
from interface.pages.home import home_page
from interface.pages.write_article import review_page
from interface.pages.article import article_page
from interface.pages.analytics import analytics_page
from interface.pages.account import account_page
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import bcrypt

# настройки подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "musicdb",
    "user": "admin",
    "password": "test",
    "host": "localhost",
    "port": "5432",
}
DB_HOST = "localhost"
DB_NAME = "musicdb"
DB_USER = "admin"
DB_PASSWORD = "test"

def get_data(query):
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            return pd.read_sql_query(query, connection)
    except Exception as e:
        st.error(f'ошибка подключения к базе данных: {e}')
        return pd.DataFrame()

st.set_page_config(
    page_title = "music project",
    page_icon = "🎵",
    layout = "wide"
)

custom_css = """
<style>
    /* Фон для вкладки */
    .stApp{
        background-color: #e4e7ed;
    }

    /* Стили для контейнера вкладок */
    .stTabs [role="tablist"] {
        display: flex;
        justify-content: space-around;
        background-color: #0e466e; /* Цвет фона вкладок */
        padding: 0.5rem;
        border-radius: 0.5rem;
    }

    /* Стили для каждой вкладки */
    .stTabs [role="tab"] {
        color: white;
        font-size: 16px;
        font-weight: bold;
        padding: 10px 20px;
        margin: 0 5px;
        cursor: pointer;
    }

    /* Стили для активной вкладки */
    .stTabs [role="tab"][aria-selected="true"] {
        background-color: #0d6eff; /* Цвет активной вкладки */
        border-radius: 5px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    /* Стили для содержимого вкладки */
    .stTabs [role="tabpanel"] {
        background-color: #6c6b70; /* Фон контента */
        padding: 20px;
        border-radius: 0 0 0.5rem 0.5rem;
        min-height: 300px; /* Высота контента */
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

def get_db_connection():
    """подключение к базе данных."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Ошибка подключения к базе данных: {e}")
        return None
    
def create_user(username, password, email):
    """добавляет нового пользователя в базу данных."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    if conn:
        try:    
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password.decode('utf-8'), email, 'user')

                )
                conn.commit()
        except Exception as e:
            st.error(f"Ошибка добавления пользователя: {e}")
        finally:
            conn.close()

def authenticate_user(username, password):
    """проверяет учетные данные пользователя."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id, username, role, password_hash FROM users WHERE username = %s",
                    (username,)
                )
                user = cur.fetchone()
                if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    return user
        except Exception as e:
            st.error(f"Ошибка авторизации: {e}")
        finally:
            conn.close()
    return None


if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_id = None

tabs = st.tabs(['Главная', 'Твоя статья', 'Рецензии', 'Жанровая аналитика', 'Аккаунт'])
with tabs[0]:
    home_page()

with tabs[1]:
    review_page()

with tabs[2]:
    article_page()

with tabs[3]:
    analytics_page()

with tabs[4]:
    account_page()
