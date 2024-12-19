import streamlit as st
import bcrypt
from psycopg2.extras import RealDictCursor
import psycopg2
import os
import subprocess

DB_HOST = "localhost"
DB_NAME = "musicdb"
DB_USER = "admin"
DB_PASSWORD = "test"

def get_db_connection():
    """Подключение к базе данных."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"ошибка подключения к базе данных: {e}")
        return None

def create_user(username, password, email, role = 'user'):
    """добавляет нового пользователя в базу данных."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    if conn:
        try:    
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password.decode('utf-8'), email, role)

                )
                conn.commit()
        except Exception as e:
            st.error(f"ошибка добавления пользователя: {e}")
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
            st.error(f"ошибка авторизации: {e}")
        finally:
            conn.close()
    return None

def delete_user(user_id):
    """удаляет пользователя (доступно только admin)."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
                st.success("Пользователь успешно удален.")
        except Exception as e:
            st.error(f"Ошибка удаления пользователя: {e}")
        finally:
            conn.close()

def list_users():
    """возвращает список всех пользователей (для admin)."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT user_id, username, email, role FROM users")
                return cur.fetchall()
        except Exception as e:
            st.error(f"ошибка загрузки пользователей: {e}")
        finally:
            conn.close()
    return []

def update_user_role(user_id, new_role):
    """обновляет роль пользователя (для admin)."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET role = %s WHERE user_id = %s", (new_role, user_id))
                conn.commit()
                st.success("Роль пользователя успешно обновлена.")
        except Exception as e:
            st.error(f"ошибка обновления роли: {e}")
        finally:
            conn.close()

def create_backup():
    try:
        # выполнение команды для создания резервной копии (пример для PostgreSQL)
        command = "pg_dump -U admin -F c -b -v -f /Users/grinya/Documents/study/s3e1/databases/music_albums_platform/backup/musicdb_backup.tar musicdb"
        subprocess.run(command, shell=True, check=True)
        st.success("Резервная копия успешно создана!")
    except subprocess.CalledProcessError:
        st.error("Ошибка при создании резервной копии!")

# функция для восстановления базы данных
def restore_backup():
    try:
        # выполнение востановления
        command = "pg_restore -U admin -d dbname -v /Users/grinya/Documents/study/s3e1/databases/music_albums_platform/backup/music_db_backup.tar"
        subprocess.run(command, shell=True, check=True)
        st.success("Данные успешно восстановлены из резервной копии!")
    except subprocess.CalledProcessError:
        st.error("Ошибка при восстановлении данных!")


def account_page():
    if st.session_state.authenticated:
        st.success(f"Вы вошли как {st.session_state.username} ({st.session_state.role})")
        if st.session_state.role == 'admin':                    #когда под входом админ
            st.header("Управление пользователями")
            users = list_users()
            if users:
                for user in users:
                    st.write(f"Имя: {user['username']}, Email: {user['email']}, Роль: {user['role']}")
                    if user['role'] != 'admin':
                        new_role = st.selectbox(f"Изменить роль для {user['username']}", ['user', 'editor', 'admin'], key=f"role_{user['user_id']}")
                        if st.button(f"Обновить роль {user['username']}", key=f"update_role_{user['user_id']}"):
                            update_user_role(user['user_id'], new_role)
                        if st.button(f"Удалить {user['username']}", key=f"delete_user_{user['user_id']}"):
                            delete_user(user['user_id'])
            
            st.header("Резервное копирование данных")
            if st.button("Создать резервную копию"):
                         create_backup()
            
            st.header("Востановление из резервной копии")
            if st.button("Восстановить из резервной копии"):
                restore_backup()

        if st.button("Выйти"):
            print("LOG: ВЫХОД ИЗ АККАУНТА")
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.user_id = None
            #st.experimental_rerun()
            st.session_state.update({"rerun": True})
    else:
        auth_tabs = st.tabs(["Вход", "Регистрация"])

        # вкладка "вход"
        with auth_tabs[0]:
            st.subheader("Вход")
            username = st.text_input("Имя пользователя", key="login_username")
            password = st.text_input("Пароль", type="password", key="login_password")
            if st.button("Войти"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.role = user['role']
                    st.session_state.user_id = user['user_id']
                    st.session_state.update({"rerun": True})
                else:
                    st.error("Неверное имя пользователя или пароль.")

        # вкладка "регистрация"
        with auth_tabs[1]:
            st.subheader("Регистрация")
            new_username = st.text_input("Имя пользователя", key="register_username")
            new_email = st.text_input("Email", key="register_email")
            new_password = st.text_input("Пароль", type="password", key="register_password")
            confirm_password = st.text_input("Подтвердите пароль", type="password", key="register_confirm_password")
            if st.button("Зарегистрироваться"):
                if new_password == confirm_password:
                    try:
                        create_user(new_username, new_password, new_email)
                        st.success("Регистрация прошла успешно. Теперь вы можете войти.")
                    except Exception as e:
                        st.error(f"Ошибка регистрации: {e}")
               