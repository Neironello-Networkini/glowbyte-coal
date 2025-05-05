import streamlit as st
import requests
import time
import pandas as pd
import json
import os
from datetime import datetime

# Настройки страницы
st.set_page_config(page_title="Выгрузки и отгрузки", page_icon="🚢", layout="wide")

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
API_URL = "http://localhost:8000/supplies"
MAX_RETRIES = 3
RETRY_DELAY = 1
LOCAL_DATA_FILE = "shipments_data.json"

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

st.title("Выгрузки и отгрузки")

# --- READ ALL ---
st.header("Список выгрузок и отгрузок")
resp = make_request("GET", f"{API_URL}/")
shipments = []

if resp:
    shipments = resp.json()
else:
    shipments = load_local_data()

if not shipments:
    st.info("Список выгрузок и отгрузок пуст")
else:
    # --- Пагинация ---
    page_size = 5
    total = len(shipments)
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
    
    # Создаем таблицу для отображения выгрузок и отгрузок
    st.table(pd.DataFrame(shipments[start:end]))
    
    st.caption(f"Страница {page} из {total_pages}")

# --- CREATE ---
st.header("Создать новую выгрузку/отгрузку")
with st.form("create_shipment"):
    col1, col2 = st.columns(2)
    
    with col1:
        brand = st.text_input("Марка", placeholder="Введите марку")
        warehouse = st.text_input("Склад", placeholder="Введите склад")
        stack = st.text_input("Штабель", placeholder="Введите штабель")
        unload_date = st.date_input("Дата выгрузки на склад")
        unload_weight = st.number_input("Вес на склад (тонны)", min_value=0.0, step=0.1)
    
    with col2:
        load_date = st.date_input("Дата погрузки на судно")
        load_weight = st.number_input("Вес на судно (тонны)", min_value=0.0, step=0.1)
    
    submitted = st.form_submit_button("Создать")
    if submitted:
        if not all([brand, warehouse, stack]):
            st.warning("Пожалуйста, заполните все обязательные поля")
        else:
            shipment_data = {
                "brand": brand,
                "warehouse": warehouse,
                "stack": stack,
                "unload_date": unload_date.isoformat(),
                "unload_weight": unload_weight,
                "load_date": load_date.isoformat() if load_date else None,
                "load_weight": load_weight
            }
            
            resp = make_request("POST", f"{API_URL}/", json=shipment_data)
            if resp and resp.status_code == 201:
                st.success("Выгрузка/отгрузка успешно создана!")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_shipments = load_local_data()
                new_id = max([s.get('id', 0) for s in local_shipments], default=0) + 1
                shipment_data['id'] = new_id
                local_shipments.append(shipment_data)
                save_local_data(local_shipments)
                st.success("Выгрузка/отгрузка успешно создана в локальном хранилище!")
                st.rerun()

# --- UPDATE ---
st.header("Редактировать выгрузку/отгрузку")
with st.form("update_shipment"):
    update_id = st.number_input("ID для обновления", min_value=1, step=1, key="update_id")
    
    col1, col2 = st.columns(2)
    
    with col1:
        update_brand = st.text_input("Марка", key="update_brand", placeholder="Введите марку")
        update_warehouse = st.text_input("Склад", key="update_warehouse", placeholder="Введите склад")
        update_stack = st.text_input("Штабель", key="update_stack", placeholder="Введите штабель")
        update_unload_date = st.date_input("Дата выгрузки на склад", key="update_unload_date")
        update_unload_weight = st.number_input("Вес на склад (тонны)", key="update_unload_weight", min_value=0.0, step=0.1)
    
    with col2:
        update_load_date = st.date_input("Дата погрузки на судно", key="update_load_date")
        update_load_weight = st.number_input("Вес на судно (тонны)", key="update_load_weight", min_value=0.0, step=0.1)
    
    update_submitted = st.form_submit_button("Обновить")
    if update_submitted:
        if not all([update_brand, update_warehouse, update_stack]):
            st.warning("Пожалуйста, заполните все обязательные поля")
        else:
            shipment_data = {
                "brand": update_brand,
                "warehouse": update_warehouse,
                "stack": update_stack,
                "unload_date": update_unload_date.isoformat(),
                "unload_weight": update_unload_weight,
                "load_date": update_load_date.isoformat() if update_load_date else None,
                "load_weight": update_load_weight
            }
            
            resp = make_request("PUT", f"{API_URL}/update/{update_id}", json=shipment_data)
            if resp and resp.status_code == 200:
                st.success("Выгрузка/отгрузка успешно обновлена")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_shipments = load_local_data()
                shipment_found = False
                for shipment in local_shipments:
                    if shipment.get('id') == update_id:
                        shipment.update(shipment_data)
                        shipment_found = True
                        break
                if shipment_found:
                    save_local_data(local_shipments)
                    st.success("Выгрузка/отгрузка успешно обновлена в локальном хранилище!")
                    st.rerun()
                else:
                    st.error("Выгрузка/отгрузка с указанным ID не найдена")

# --- DELETE ---
st.header("Удалить выгрузку/отгрузку")
with st.form("delete_shipment"):
    delete_id = st.number_input("ID для удаления", min_value=1, step=1, key="delete_id")
    delete_submitted = st.form_submit_button("Удалить")
    if delete_submitted:
        if st.warning("Вы уверены, что хотите удалить эту выгрузку/отгрузку?"):
            resp = make_request("DELETE", f"{API_URL}/delete/{delete_id}")
            if resp and resp.status_code == 200:
                st.success("Выгрузка/отгрузка успешно удалена")
                st.rerun()
            elif resp:
                st.error(f"Ошибка: {resp.text}")
            else:
                # Работа с локальными данными
                local_shipments = load_local_data()
                initial_length = len(local_shipments)
                local_shipments = [s for s in local_shipments if s.get('id') != delete_id]
                if len(local_shipments) < initial_length:
                    save_local_data(local_shipments)
                    st.success("Выгрузка/отгрузка успешно удалена из локального хранилища!")
                    st.rerun()
                else:
                    st.error("Выгрузка/отгрузка с указанным ID не найдена") 