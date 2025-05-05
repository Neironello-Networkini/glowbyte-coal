import streamlit as st
import pandas as pd
import os
import datetime
import random

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

params = st.query_params
selected_date = params.get("date", "Не указана")
shabel_id = params.get("shabel_id", "Не указан")

st.title("Детали возгорания")
st.write(f"Дата возможного возгорания: {selected_date}")
st.write(f"ID штабе́ля: {shabel_id}")

# Отображение основной информации
st.markdown(f"""
<div style="padding: 20px; background-color: #fdf0f0; border-radius: 12px; margin-bottom: 20px;">
    <h3>📅 Дата возгорания: <span style="color: red;">{selected_date}</span></h3>
    <h4>🏗️ Штабель ID: {shabel_id}</h4>
</div>
""", unsafe_allow_html=True)

# --- Причины возгорания (заглушка) ---
st.subheader("Причины возможного возгорания:")
reasons = [
    "📌 Повышенная температура в ядре штабеля",
    "📌 Недостаточная вентиляция",
    "📌 Влажность выше нормы",
    "📌 Истечение срока хранения",
    "📌 Химические реакции внутри штабеля"
]
st.write("\n".join(reasons))

# --- График температуры (заглушка) ---
st.subheader("📈 Динамика температуры (последние 10 дней)")

def generate_temperature_data():
    dates = pd.date_range(end=datetime.date.today(), periods=10)
    temps = [random.uniform(35.0, 80.0) for _ in range(10)]
    return pd.DataFrame({"Дата": dates, "Температура (°C)": temps})

temp_data = generate_temperature_data()
st.line_chart(temp_data.set_index("Дата"))

# --- Другие метрики (заглушка) ---
st.subheader("📊 Дополнительные показатели:")

col1, col2, col3 = st.columns(3)
col1.metric("Макс. температура", f"{max(temp_data['Температура (°C)']):.1f} °C")
col2.metric("Средняя температура", f"{temp_data['Температура (°C)'].mean():.1f} °C")
col3.metric("Дней до возгорания", "≈ 5 дней")  # Здесь можно подставлять значение из ML модели

# --- Подключение CSS стилей (если есть) ---
style_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(style_path):
    with open(style_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Навигация ---


