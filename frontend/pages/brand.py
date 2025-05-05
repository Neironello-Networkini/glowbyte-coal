import streamlit as st
import requests
import time
import pandas as pd
import json
import os

# Настройки страницы
st.set_page_config(page_title="Управление марками угля", page_icon="🏷️", layout="wide")

# Подключаем стили
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Конфигурация API
API_URL = "http://localhost:8000/brand"
MAX_RETRIES = 3
RETRY_DELAY = 1
LOCAL_DATA_FILE = "brands_data.json"

# Функция для работы с локальными данными
def load_local_data():
    if os.path.exists(LOCAL_DATA_FILE):
        with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

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

st.title("Управление марками угля")

# --- READ ALL ---
st.header("Список марок")
resp = make_request("GET", f"{API_URL}/")
brands = []

if resp:
    brands = resp.json()
else:
    brands = load_local_data()

if not brands:
    st.info("Список марок пуст")
else:
    # --- Пагинация ---
    page_size = 5
    total = len(brands)
    total_pages = (total + page_size - 1) // page_size

    page = st.number_input(
        "Страница",
        min_value=1,
        max_value=max(1, total_pages),
        value=1,
        step=1
    )

    start = (page - 1) * page_size
    end = start + page_size
    
    # Создаем таблицу для отображения марок
    st.table(pd.DataFrame(brands[start:end]))
    
    st.caption(f"Страница {page} из {total_pages}")

# --- CREATE ---
st.header("Создать новую марку")
with st.form("create_brand"):
    new_brand_name = st.text_input("Название марки", placeholder="Введите название марки")
    submitted = st.form_submit_button("Создать")
    if submitted:
        if not new_brand_name.strip():
            st.warning("Пожалуйста, введите название марки")
        else:
            resp = make_request("POST", f"{API_URL}/", json={"name": new_brand_name})
            if resp and resp.status_code == 201:
                st.success("Марка успешно создана!")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_brands = load_local_data()
                new_id = max([b.get('id', 0) for b in local_brands], default=0) + 1
                local_brands.append({"id": new_id, "name": new_brand_name})
                save_local_data(local_brands)
                st.success("Марка успешно создана в локальном хранилище!")
                st.rerun()

# --- UPDATE ---
st.header("Редактировать марку")
with st.form("update_brand"):
    update_id = st.number_input("ID марки для обновления", min_value=1, step=1, key="update_id")
    update_name = st.text_input("Новое название марки", key="update_name", placeholder="Введите новое название")
    update_submitted = st.form_submit_button("Обновить")
    if update_submitted:
        if not update_name.strip():
            st.warning("Пожалуйста, введите новое название марки")
        else:
            resp = make_request("PUT", f"{API_URL}/update/{update_id}", json={"name": update_name})
            if resp and resp.status_code == 200:
                st.success("Марка успешно обновлена")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_brands = load_local_data()
                brand_found = False
                for brand in local_brands:
                    if brand.get('id') == update_id:
                        brand['name'] = update_name
                        brand_found = True
                        break
                if brand_found:
                    save_local_data(local_brands)
                    st.success("Марка успешно обновлена в локальном хранилище!")
                    st.rerun()
                else:
                    st.error("Марка с указанным ID не найдена")

# --- DELETE ---
st.header("Удалить марку")
with st.form("delete_brand"):
    delete_id = st.number_input("ID марки для удаления", min_value=1, step=1, key="delete_id")
    delete_submitted = st.form_submit_button("Удалить")
    if delete_submitted:
        if st.warning("Вы уверены, что хотите удалить эту марку?"):
            resp = make_request("DELETE", f"{API_URL}/delete/{delete_id}")
            if resp and resp.status_code == 200:
                st.success("Марка успешно удалена")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_brands = load_local_data()
                initial_length = len(local_brands)
                local_brands = [b for b in local_brands if b.get('id') != delete_id]
                if len(local_brands) < initial_length:
                    save_local_data(local_brands)
                    st.success("Марка успешно удалена из локального хранилища!")
                    st.rerun()
                else:
                    st.error("Марка с указанным ID не найдена")