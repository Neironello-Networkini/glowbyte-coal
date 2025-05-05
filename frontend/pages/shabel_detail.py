import streamlit as st
import pandas as pd
import os
import datetime
import calendar
import requests

# Настройки страницы
st.set_page_config(page_title="FireWatch", page_icon="🔥", layout="wide")

# Подключаем стили
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Шапка сайта
def header():
    st.markdown("""
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
    """, unsafe_allow_html=True)

header()

# Получение даты из параметров запроса
params = st.query_params
selected_date = params.get("date", "Не указана")

API_URL = "http://localhost:8000/stack"

# Получение ID штабеля из параметра
shabel_id = params.get("stack_id", [None])

if shabel_id is not None:
    try:
        shabel_id_int = int(shabel_id)
        resp = requests.get(f"{API_URL}/{shabel_id_int}")
        print(resp.json())
        if resp.status_code == 200 and resp.json():
            stack = resp.json()
            st.title(f"Штабель {stack.get('name', '')} (id {stack.get('id', '')})")
            st.markdown(f"""
            <div style="padding: 20px; background-color: #ffffff; border-radius: 12px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h3>Краткая информация:</h3>
                <p><strong>Склад:</strong> {stack.get('warehouse_name')} (id {stack.get('warehouse_id')})</p>
            </div>
            """, unsafe_allow_html=True)
            # Можно добавить вывод других полей stack
        else:
            st.error("Штабель не найден.")
    except Exception as e:
        st.error(f"Ошибка: {e}")
else:
    st.error("ID штабеля не указан в параметрах URL.")

today = datetime.date.today()

# Календарь

def render_calendar(year, month, fires_by_day):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    html = f"""
    <div class='calendar-wrapper'>
        <h2 style='text-align: center;'>Календарь предсказания самовозгораний</h2>
        <h3 style='text-align: center;'>{month_name} {year}</h3>
        <table class='calendar'>
    """

    html += "<tr>" + "".join(
        f"<th class='center'>{day}</th>" for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    ) + "</tr>"

    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td class='day empty'></td>"
            else:
                classes = "day"
                label = str(day)
                if day == today.day and month == today.month and year == today.year:
                    classes += " today"
                if day in fires_by_day:
                    count = fires_by_day[day]
                    label = f"<a href='/day?day={year}-{month:02d}-{day:02d}' class='calendar-link'>{label}<br><span class='fire-count past'>{count} 🔥</span></a>"
                    html += f"<td class='{classes}'>{label}</td>"
                else:
                    html += f"<td class='{classes}'>{label}</td>"
        html += "</tr>"

    html += "</table></div>"
    return html

# Выбор года и месяца
col1, col2 = st.columns([1, 3])
with col1:
    year = st.selectbox("Выберите год", list(range(2018, today.year + 1)), index=today.year - 2018)
with col2:
    month_name_list = list(calendar.month_name)[1:]
    if year == today.year:
        available_months = month_name_list[:min(today.month + 1, 12)]
    else:
        available_months = month_name_list
    month_name_selected = st.selectbox("Выберите месяц", available_months, index=min(today.month - 1, len(available_months) - 1))
    month = available_months.index(month_name_selected) + 1

# Получаем предикты с сервера
try:
    resp = requests.get(f"http://localhost:8000/predict/stack/{shabel_id}/{year}/{month}")
    resp.raise_for_status()
    predictions = resp.json()
except Exception as e:
    st.error(f"Ошибка получения данных с сервера: {e}")
    predictions = []

fires_by_day = {}
for pred in predictions:
    day = int(pred['date'].split('-')[2])
    fires_by_day.setdefault(day, 0)
    fires_by_day[day] += 1

# Отображение календаря
calendar_html = render_calendar(year, month, fires_by_day)
st.markdown(calendar_html, unsafe_allow_html=True)

st.markdown("""
<style>
.day.today {
    border: 2px solid red;
    border-radius: 8px;
}
.calendar-link {
    text-decoration: none;
    color: black;
    display: block;
    width: 100%;
    height: 100%;
}
.fire-count {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-top: 4px;
}
.fire-count.past {
    background-color: #ffebee;
    color: #d32f2f;
}
.fire-count.future {
    background-color: #fff3e0;
    color: #f57c00;
}
</style>
""", unsafe_allow_html=True)
