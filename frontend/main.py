import streamlit as st
import pandas as pd
import datetime
import calendar
import requests
from urllib.parse import parse_qs

API_URL = "http://localhost:8000/predict"  # Укажите ваш адрес FastAPI

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
            <a class="nav-item" href="/help">Справка</a>  <!-- Ссылка на справку -->
        </div>
    </div>
    """, unsafe_allow_html=True)

header()

# Примерные данные
# past_fires = {
#     5: [
#         {"Название": "Штабель A", "Состояние": "Сгорел полностью"},
#         {"Название": "Штабель B", "Состояние": "Повреждён"}
#     ],
#     12: [
#         {"Название": "Штабель C", "Состояние": "Сгорел частично"}
#     ],
#     17: [
#         {"Название": "Штабель D", "Состояние": "Сгорел полностью"},
#         {"Название": "Штабель E", "Состояние": "Сгорел частично"},
#         {"Название": "Штабель F", "Состояние": "Сгорел полностью"}
#     ]
# }

# future_fires = {}
# for i in range(1, 4):
#     day = (today + datetime.timedelta(days=i)).day
#     future_fires[day] = [
#         {"Название": f"Штабель {chr(88+i)}", "Прогноз": "Высокий риск"}
#         for _ in range(i)
#     ]

# query_params = st.experimental_get_query_params()
# date_param = query_params.get("day", [None])[0]

# if date_param:
#     # Парсим дату
#     try:
#         year, month, day = map(int, date_param.split('-'))
#         st.header(f"Пожары за {date_param}")

#         # Запрос к API
#         API_URL = "http://localhost:8000/predict"
#         try:
#             resp = requests.get(f"{API_URL}/{year}/{month}/{day}")
#             resp.raise_for_status()
#             fires = resp.json()
#         except Exception as e:
#             st.error(f"Ошибка получения данных с сервера: {e}")
#             fires = []

#         if not fires:
#             st.info("Нет пожаров в этот день.")
#         else:
#             df = pd.DataFrame(fires)
#             st.dataframe(df)
#     except Exception as e:
#         st.error(f"Некорректная дата: {e}")
#     st.stop()
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
    resp = requests.get(f"{API_URL}/{year}/{month}")
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
