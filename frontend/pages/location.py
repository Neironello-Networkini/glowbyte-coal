import streamlit as st
import requests
import time
import json
import os

# Настройки страницы
st.set_page_config(page_title="Установка местоположения территории", page_icon="📍", layout="wide")


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


# Подключаем стили
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Конфигурация API
API_URL = "http://localhost:8000/location"
MAX_RETRIES = 3
RETRY_DELAY = 1
LOCAL_DATA_FILE = "location_data.json"

# Функция для работы с локальными данными
def load_local_data():
    if os.path.exists(LOCAL_DATA_FILE):
        with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"latitude": 0.0, "longitude": 0.0}  # Значения по умолчанию

def save_local_data(data):
    with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def make_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.warning("Сервер недоступен. Работаем с локальными данными.")
        return None

st.title("Установка местоположения территории")

# --- READ CURRENT LOCATION ---
st.header("Текущее местоположение")
resp = make_request("GET", f"{API_URL}/")
location_data = {}

if resp:
    location_data = resp.json()
else:
    location_data = load_local_data()

if location_data:
    st.info(f"""
    Текущие координаты:
    - Широта: {location_data.get('latitude', 0.0)}°
    - Долгота: {location_data.get('longitude', 0.0)}°
    """)

# --- UPDATE LOCATION ---
st.header("Изменить местоположение")
with st.form("update_location"):
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input(
            "Широта (°)",
            min_value=-90.0,
            max_value=90.0,
            value=location_data.get('latitude', 0.0),
            step=0.000001,
            format="%.6f",
            help="Введите значение от -90 до 90 градусов"
        )
    
    with col2:
        longitude = st.number_input(
            "Долгота (°)",
            min_value=-180.0,
            max_value=180.0,
            value=location_data.get('longitude', 0.0),
            step=0.000001,
            format="%.6f",
            help="Введите значение от -180 до 180 градусов"
        )
    
    submitted = st.form_submit_button("Обновить местоположение")
    if submitted:
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        resp = make_request("PUT", f"{API_URL}/update", json=location_data)
        if resp and resp.status_code == 200:
            st.success("Местоположение успешно обновлено!")
            st.rerun()
        elif resp:
            st.error(f"Ошибка: {resp.text}")
        else:
            # Работа с локальными данными
            save_local_data(location_data)
            st.success("Местоположение успешно обновлено в локальном хранилище!")
            st.rerun()

# Информация о формате координат
st.markdown("""
### Информация о формате координат
- Широта (latitude): от -90° до 90°
  - Положительные значения для северной широты
  - Отрицательные значения для южной широты
- Долгота (longitude): от -180° до 180°
  - Положительные значения для восточной долготы
  - Отрицательные значения для западной долготы

Примеры координат:
- Москва: 55.7558° с.ш., 37.6173° в.д.
- Санкт-Петербург: 59.9343° с.ш., 30.3351° в.д.
""") 