import streamlit as st
import requests
import time
import pandas as pd
import json
import os

# Настройки страницы
st.set_page_config(page_title="Управление складами", page_icon="🏢", layout="wide")

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
API_URL = "http://localhost:8000/warehouse"
MAX_RETRIES = 3
RETRY_DELAY = 1
LOCAL_DATA_FILE = "warehouses_data.json"

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

st.title("Управление складами")

# --- READ ALL ---
st.header("Список складов")
resp = make_request("GET", f"{API_URL}/")
warehouses = []

if resp:
    warehouses = resp.json()
else:
    warehouses = load_local_data()

if not warehouses:
    st.info("Список складов пуст")
else:
    # --- Пагинация ---
    page_size = 5
    total = len(warehouses)
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
    
    # Создаем таблицу для отображения складов
    st.table(pd.DataFrame(warehouses[start:end]))
    
    st.caption(f"Страница {page} из {total_pages}")

# --- CREATE ---
st.header("Создать новый склад")
with st.form("create_warehouse"):
    new_warehouse_name = st.text_input("Название склада", placeholder="Введите название склада")
    submitted = st.form_submit_button("Создать")
    if submitted:
        if not new_warehouse_name.strip():
            st.warning("Пожалуйста, введите название склада")
        else:
            resp = make_request("POST", f"{API_URL}/", json={"name": new_warehouse_name})
            if resp and resp.status_code == 201:
                st.success("Склад успешно создан!")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_warehouses = load_local_data()
                new_id = max([w.get('id', 0) for w in local_warehouses], default=0) + 1
                local_warehouses.append({"id": new_id, "name": new_warehouse_name})
                save_local_data(local_warehouses)
                st.success("Склад успешно создан в локальном хранилище!")
                st.rerun()

# --- UPDATE ---
st.header("Редактировать склад")
with st.form("update_warehouse"):
    update_id = st.number_input("ID склада для обновления", min_value=1, step=1, key="update_id")
    update_name = st.text_input("Новое название склада", key="update_name", placeholder="Введите новое название")
    update_submitted = st.form_submit_button("Обновить")
    if update_submitted:
        if not update_name.strip():
            st.warning("Пожалуйста, введите новое название склада")
        else:
            resp = make_request("PUT", f"{API_URL}/update/{update_id}", json={"name": update_name})
            if resp and resp.status_code == 200:
                st.success("Склад успешно обновлен")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_warehouses = load_local_data()
                warehouse_found = False
                for warehouse in local_warehouses:
                    if warehouse.get('id') == update_id:
                        warehouse['name'] = update_name
                        warehouse_found = True
                        break
                if warehouse_found:
                    save_local_data(local_warehouses)
                    st.success("Склад успешно обновлен в локальном хранилище!")
                    st.rerun()
                else:
                    st.error("Склад с указанным ID не найден")

# --- DELETE ---
st.header("Удалить склад")
with st.form("delete_warehouse"):
    delete_id = st.number_input("ID склада для удаления", min_value=1, step=1, key="delete_id")
    delete_submitted = st.form_submit_button("Удалить")
    if delete_submitted:
        if st.warning("Вы уверены, что хотите удалить этот склад?"):
            resp = make_request("DELETE", f"{API_URL}/delete/{delete_id}")
            if resp and resp.status_code == 200:
                st.success("Склад успешно удален")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_warehouses = load_local_data()
                initial_length = len(local_warehouses)
                local_warehouses = [w for w in local_warehouses if w.get('id') != delete_id]
                if len(local_warehouses) < initial_length:
                    save_local_data(local_warehouses)
                    st.success("Склад успешно удален из локального хранилища!")
                    st.rerun()
                else:
                    st.error("Склад с указанным ID не найден") 