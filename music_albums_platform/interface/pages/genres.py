import streamlit as st
import psycopg2
from io import BytesIO
#страница рецензи   

def connect_db():
    return psycopg2.connect(
        dbname="musicdb",
        user="admin",
        password="test",
        host="localhost",
        port="5432"
    )

def get_reviews():
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT reviews.review_id, reviews.rating, reviews.review_text, 
                TO_CHAR(reviews.created_at, 'YYYY-MM-DD HH24:MI') AS created_at, 
                       albums.title AS album_title, users.username AS user_name, albums.cover_image
                FROM reviews
                JOIN albums ON reviews.album_id = albums.album_id
                JOIN users ON reviews.user_id = users.user_id
                ORDER BY reviews.created_at DESC;
            """)
            return cursor.fetchall()


def get_review_details(review_id):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
               SELECT reviews.rating, 
                       reviews.review_text, 
                       TO_CHAR(reviews.created_at, 'YYYY-MM-DD HH24:MI') AS created_at, 
                       albums.title AS album_title, 
                       users.username AS user_name, 
                       albums.cover_image
                FROM reviews
                JOIN albums ON reviews.album_id = albums.album_id
                JOIN users ON reviews.user_id = users.user_id
                WHERE reviews.review_id = %s; 
            """, (review_id,))
            return cursor.fetchone()

def display_cover_image(cover_image_data, size="small"):
    if cover_image_data:
        #преобразуем байты в изображение
        cover_image = BytesIO(cover_image_data)
        if size == "small":
            st.image(cover_image, width=150)  # уменьшенное изображение
        elif size == "large":
            st.image(cover_image, width=400)  # увеличенное изображение
    else:
        st.text("Обложка отсутствует.")
    
def article_page():
    st.title('Рецензии')
    st.write('Ваши статьи тут')
    if "selected_review_id" not in st.session_state:
        st.session_state.selected_review_id = None

    #еЖсли выбран конкретный отзыв
    if st.session_state.selected_review_id:
        review_details = get_review_details(st.session_state.selected_review_id)
        if review_details:
            st.title(f"Рецензия на альбом: {review_details[3]}")  # album_title
            st.subheader(f"Автор: {review_details[4]}")  # user_name
            st.write(f"Рейтинг: {review_details[0]} из 10")  # rating
            st.write(f"Дата создания: {review_details[2]}")  # created_at
            st.markdown(f"### Текст рецензии:\n{review_details[1]}")  # review_text
            
            if review_details[5]:
                #st.markdown("### Обложка альбома:")
                display_cover_image(review_details[5], size='large')  # cover_image
            if st.button("Назад к списку рецензий"):
                st.session_state.selected_review_id = None
        else:
            st.error("Рецензия не найдена.")
    else:
        st.title("Список рецензий")
        reviews = get_reviews()
        if reviews:
            for review in reviews:
                st.subheader(f"Рецензия на альбом: {review[4]}")  # album_title
                st.write(f"Автор: {review[5]}")  # user_name
                st.write(f"Рейтинг: {review[1]} из 10")  # rating
                st.write(f"Дата создания: {review[3]}")  # created_at
                st.write(review[2][:200] + "..." if len(review[2]) > 200 else review[2])  # review_text
                if review[6]:
                    #st.markdown("### Обложка альбома:")
                    display_cover_image(review[6], size='small')  # cover_image
                if st.button("Читать полностью", key=f"review_{review[0]}"):
                    st.session_state.selected_review_id = review[0]
        else:
            st.write("Рецензий пока нет.")