import streamlit as st
import pandas as pd
import os
import datetime
import requests

API_URL = "http://localhost:8000/stack"

# Настройки страницы
st.set_page_config(page_title="FireWatch", page_icon="🔥", layout="wide")

# Подключаем стили
style_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
with open(style_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Шапка сайта
def header():
    st.markdown("""
    <div class="site-header">
        <div class="logo">🔥 FireWatch</div>
        <div class="nav">
            <a class="nav-item" href="/">Главная</a>
            <a class="nav-item active" href="/stack">Штабели</a>
            <a class="nav-item" href="/warehouse">Склады</a>
            <a class="nav-item" href="/shipments">Выгрузки и отгрузки</a>
            <a class="nav-item" href="/location">Местоположение</a>
            <a class="nav-item" href="/help">Справка</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

header()

# Заглушка для данных штабелей
# def get_shabels_data():
#     # Имитируем данные, которые должны быть в базе данных
#     shabel_data = [
#         {"ID": 1, "Название": "Штабель 1", "Сформирован": "2023-04-01", "Ближайшее возгорание": "2023-05-10",
#          "Макс. температура": "450°C", "Склад": 5},
#         {"ID": 2, "Название": "Штабель 5774", "Сформирован": "2023-04-15", "Ближайшее возгорание": "2023-06-20",
#          "Макс. температура": "500°C", "Склад": 4},
#         {"ID": 3, "Название": "Штабель 3", "Сформирован": "2023-05-01", "Ближайшее возгорание": "2023-07-30",
#          "Макс. температура": "480°C", "Склад": 2},
#         {"ID": 4, "Название": "Штабель 4", "Сформирован": "2023-06-05", "Ближайшее возгорание": "2023-08-25",
#          "Макс. температура": "470°C", "Склад": 3},
#         {"ID": 5, "Название": "Штабель 5", "Сформирован": "2023-06-10", "Ближайшее возгорание": "2023-09-12",
#          "Макс. температура": "460°C", "Склад": 1}
#     ]

#     # Преобразуем список в DataFrame
#     return pd.DataFrame(shabel_data)


def fetch_stacks():
    try:
        resp = requests.get(f"{API_URL}/")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"Ошибка получения данных с сервера: {e}")
        return []

# Заголовок + форма добавления
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px;">
    <h1>Список штабелей</h1>
</div>
""", unsafe_allow_html=True)

# Форма добавления нового штабеля
st.markdown("""
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h3>Добавить новый штабель</h3>
</div>
""", unsafe_allow_html=True)

with st.form("new_stack_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        stack_name = st.text_input("Название штабеля", placeholder="Например: Штабель 1")
    with col2:
        warehouse = st.text_input("Название склада", placeholder="Например: Склад 1")
        
    
    submit_button = st.form_submit_button("Добавить штабель")
    
    if submit_button:
        if stack_name and warehouse:
            payload = {
                "name": stack_name,
                "warehouse": warehouse
            }
            try:
                resp = requests.post(f"{API_URL}/", json=payload)
                if resp.status_code == 200:
                    st.success("Штабель успешно добавлен!")
                    st.rerun()
                else:
                    st.error(f"Ошибка: {resp.text}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")
        else:
            st.error("Пожалуйста, заполните все поля")

# Фильтры и поиск
st.markdown("""
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h3>Фильтры и поиск</h3>
</div>
""", unsafe_allow_html=True)

# Создаем колонки для фильтров
col1, col2, col3 = st.columns(3)

with col2:
    search_query = st.text_input("Поиск по названию", placeholder="Введите название штабеля")

with col1:
    id_filter = st.text_input("Фильтр по ID", placeholder="Введите ID")

with col3:
    warehouse_filter = st.text_input("Фильтр по складу", placeholder="Введите номер склада")

# Применяем фильтры
stacks_data = fetch_stacks()
if not stacks_data:
    st.info("Нет данных о штабелях")
    st.stop()
df_stacks = pd.DataFrame(stacks_data)

filtered_df = df_stacks.copy()

if search_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False, na=False)]

if id_filter:
    filtered_df = filtered_df[filtered_df['id'].astype(str).str.contains(id_filter)]

if warehouse_filter:
    filtered_df = filtered_df[filtered_df['warehouse_id'].astype(str).str.contains(warehouse_filter)]

# Отображаем отфильтрованный список штабелей
st.markdown("""
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h3>Список штабелей</h3>
</div>
""", unsafe_allow_html=True)

st.dataframe(filtered_df)

# Кнопка для скачивания таблицы в формате CSV
csv = filtered_df.to_csv(index=False)  # Преобразуем таблицу в CSV
st.download_button(
    label="Скачать таблицу штабелей",
    data=csv,
    file_name="stack.csv",
    mime="text/csv"
)

st.header("Загрузить штабели из CSV")
with st.form("upload_stack_csv"):
    csv_file = st.file_uploader("Выберите CSV-файл со штабелями", type=["csv"])
    upload_submitted = st.form_submit_button("Загрузить")
    if upload_submitted and csv_file is not None:
        try:
            files = {"file": (csv_file.name, csv_file.getvalue(), "text/csv")}
            resp = requests.post(f"{API_URL}/upload", files=files)
            if resp.status_code == 201:
                st.success("Штабели успешно загружены!")
                st.rerun()
            else:
                st.error(f"Ошибка: {resp.text}")
        except Exception as e:
            st.error(f"Ошибка загрузки CSV: {e}")

st.header("Поиск штабеля по ID")
search_id = st.number_input("Введите ID штабеля", min_value=1, step=1)
if st.button("Найти штабель"):
    try:
        resp = requests.get(f"{API_URL}/{search_id}")
        if resp.status_code == 200 and resp.json():
            st.json(resp.json())
        else:
            st.warning("Штабель не найден")
    except Exception as e:
        st.error(f"Ошибка соединения: {e}")

st.markdown("""
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h3>Удаление штабеля</h3>
</div>
""", unsafe_allow_html=True)

for idx, row in filtered_df.iterrows():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"ID: {row['id']} | Название: {row['name']} | Склад: {row.get('warehouse_name', row.get('warehouse_id', ''))}")
    with col2:
        if st.button("Удалить", key=f"delete_{row['id']}"):
            try:
                resp = requests.delete(f"{API_URL}/{row['id']}")
                if resp.status_code == 200:
                    st.success(f"Штабель {row['name']} удалён!")
                    st.rerun()
                else:
                    st.error(f"Ошибка: {resp.text}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")


