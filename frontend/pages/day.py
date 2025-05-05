import streamlit as st
import pandas as pd
import datetime
import requests

# URL вашего API для предсказаний пожаров
API_URL = "http://localhost:8000/predict"

# Получаем параметры запроса из URL
# query_params = st.experimental_get_query_params()
# date_param = query_params.get("day", [None])[0]

# Настройки страницы
st.set_page_config(
    page_title="FireWatch",
    page_icon="🔥",
    layout="wide",
)

# Подключаем стили
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Шапка сайта
def header():
    st.markdown(
        """
        <div class="site-header">
            <div class="logo">🔥 FireWatch</div>
            <div class="nav">
                <a class="nav-item" href="/">Главная</a>
                <a class="nav-item" href="/stack">Штабели</a>
                <a class="nav-item" href="/warehouse">Склады</a>
                <a class="nav-item" href="/shipments">Выгрузки и отгрузки</a>
                <a class="nav-item" href="/location">Местоположение</a>
                <a class="nav-item" href="/help">Справка</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

header()


# Сегодняшний день
today = datetime.date.today()

# Заголовок и разделитель
st.title("Предсказание воспламенения дня")
st.markdown("""<hr style="border:1px solid #e0e0e0; margin:20px 0;">""", unsafe_allow_html=True)

# Параметры даты из URL
params = st.experimental_get_query_params()
date_param = params.get("day", [None])[0]

if date_param:
    try:
        y, m, d = map(int, date_param.split('-'))
        selected_date = datetime.date(y, m, d)
        # Если в URL передан параметр day=YYYY-MM-DD, выводим реальные пожары
        st.header(f"Пожары за {date_param}")

        # Запрос к API
        try:
            resp = requests.get(f"{API_URL}/{y}/{m}/{d}")
            resp.raise_for_status()
            fires = resp.json()  # ожидаем список dict с ключами 'id', 'name', 'warehouse'
        except Exception as e:
            st.error(f"Ошибка получения данных с сервера: {e}")
            fires = []

        if not fires:
            st.info("Нет пожаров в этот день.")
        else:
            st.subheader("Список пожаров:")
            for fire in fires:
                sid = fire.get("stack_id")
                name = fire.get("stack_name", "—")
                wh = fire.get("warehouse_name", "—")
                weight = fire.get("weight", "—")
                st.markdown(
                    f"- 🔥 **Штабель {name}** (Склад {wh}), "
                    f"Вес по акту: {weight} тонн. "
                    f"[Подробнее (ID: {sid})](/shabel_detail?stack_id={sid})"
                )

    except Exception as e:
        st.error(f"Некорректная дата: {e}")

    st.stop()
else:
    st.info("Дата не выбрана.")
