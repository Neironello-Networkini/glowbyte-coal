# pages/help.py
import streamlit as st

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

# Содержание
st.markdown("""
<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>Содержание</h2>
    <ul>
        <li><a href="#general">1. Общая информация</a></li>
        <li><a href="#main">2. Главная страница</a></li>
        <li><a href="#stacks">3. Управление штабелями</a></li>
        <li><a href="#warehouses">4. Управление складами</a></li>
        <li><a href="#shipments">5. Выгрузки и отгрузки</a></li>
        <li><a href="#location">6. Местоположение</a></li>
        <li><a href="#faq">8. Часто задаваемые вопросы</a></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 1. Общая информация
st.markdown("""
<div id="general" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>1. Общая информация</h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
**FireWatch** — это система для мониторинга и управления штабелями угля на складах. Система помогает:
- Следить за состоянием штабелей
- Управлять складами и их загрузкой
- Контролировать процессы выгрузки и отгрузки
- Отслеживать местоположение объектов
- Формировать подробные отчёты и аналитику

**Кому полезно:**
- Операторам складов
- Руководителям производств
- Аналитикам и инженерам

**Совет:** Всегда используйте верхнее меню для быстрого перехода между разделами.
""")

# 2. Главная страница
st.markdown("""
<div id="main" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>2. Главная страница</h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
На главной странице вы увидите:

- **[Календарь предсказания самовозгораний](/)**  
  В календаре отображаются дни, когда были пожары, и количество штабелей, которые горели в этот день.  
  Каждый день с пожаром — кликабелен.  
  При нажатии вы перейдёте на страницу [«Предсказание воспламенения дня»](/day), где увидите список штабелей, которые могут загореться.

---

### Страница «Предсказание воспламенения дня»
На этой странице отображается список штабелей, которые могут загореться в выбранный день.  
Каждый штабель в этом списке также кликабелен и ведёт на страницу с информацией о конкретном штабеле ([пример страницы](/shabel_detail?shabel_id=1)).

---

### Страница конкретного штабеля
На странице штабеля отображается календарь предсказания самовозгораний для этого штабеля.  
Ниже календаря можно добавлять измерения температуры для выбранного штабеля.

---

**Навигация по шапке профиля**  
В верхнем меню доступны переходы в разделы:
- [Штабели](/stack)
- [Склады](/warehouse)
- [Выгрузки и отгрузки](/shipments)
- [Местоположение](/location)
- [Справка](/help)
""")

# 3. Управление штабелями
st.markdown("""
<div id="stacks" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>3. <a href='/stack' target='_self'>Управление штабелями</a></h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
**Возможности раздела:**
- Просмотр списка всех штабелей
- Добавление нового штабеля
- Редактирование и удаление существующих
- Фильтрация и поиск по названию, ID, складу
- Экспорт списка в CSV

**Пошаговая инструкция:**
1. Для добавления нажмите **Добавить штабель**, заполните все поля и подтвердите.
2. Для редактирования найдите нужный штабель и нажмите ✏️, внесите изменения и сохраните.
3. Для удаления нажмите 🗑️ рядом с нужным штабелем.
4. Используйте фильтры сверху для быстрого поиска.
5. Для экспорта нажмите **Скачать таблицу штабелей** внизу страницы.

**Советы:**
- Все изменения применяются мгновенно.
- Если не видите новый штабель — обновите страницу.

**Типовой сценарий:**
- Добавьте штабель, затем сразу отфильтруйте его по номеру склада.
""")

# 4. Управление складами
st.markdown("""
<div id="warehouses" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>4. <a href='/warehouse' target='_self'>Управление складами</a></h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
В разделе "Склады" вы можете:

- Просматривать список всех складов.
- Добавлять новый склад с указанием его номера и/или названия.
- Редактировать информацию о складе (например, изменить номер или название).
- Удалять склад из списка.
- Использовать фильтр для быстрого поиска нужного склада.

**Пошаговая инструкция:**
1. Для добавления склада нажмите кнопку **Добавить склад** и заполните форму.
2. Для редактирования используйте кнопку ✏️ рядом со складом.
3. Для удаления — кнопку 🗑️.
4. Для поиска используйте фильтр по номеру или названию склада.
""")

# 5. Выгрузки и отгрузки
st.markdown("""
<div id="shipments" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>5. <a href='/shipments' target='_self'>Выгрузки и отгрузки</a></h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
**Возможности раздела:**
- Регистрация новых выгрузок и отгрузок
- Просмотр истории операций
- Фильтрация по дате, складу, типу операции

**Пошаговая инструкция:**
1. Для регистрации выберите **Новая выгрузка** или **Новая отгрузка**.
2. Заполните все поля: дата, время, номер вагона, тип угля, количество, склад.
3. Нажмите **Сохранить**.
4. Для просмотра истории используйте фильтры и сортировку.

**Советы:**
- Проверяйте правильность введённых данных перед сохранением.
- Используйте историю для анализа эффективности работы склада.

**Типовой сценарий:**
- Зарегистрируйте выгрузку, затем проверьте, что она появилась в истории.
""")

# 6. Местоположение
st.markdown("""
<div id="location" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>6. <a href='/location' target='_self'>Местоположение</a></h2>
</div>
""", unsafe_allow_html=True)
st.markdown("Найдите на карте свои долготу и широту.")

# 8. Часто задаваемые вопросы (FAQ)
st.markdown("""
<div id="faq" style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
    <h2>8. Часто задаваемые вопросы (FAQ)</h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
- **Как быстро найти нужный штабель или склад?**  
  Используйте фильтры и поиск в соответствующем разделе.
- **Что делать, если страница не загружается?**  
  Попробуйте обновить страницу или очистить кэш браузера.
- **Как восстановить удалённый штабель?**  
  В текущей версии восстановление невозможно — будьте внимательны при удалении.
- **Как связаться с поддержкой?**  
  Используйте контактную информацию на главной странице или обратитесь к администратору.
- **Можно ли работать с сайтом с телефона?**  
  Да, сайт адаптирован для мобильных устройств, но удобнее работать с компьютера.

---
**Навигация:** [К содержанию](#general)
""")

# Кнопка возврата к содержанию
st.markdown("""
<div style="position: fixed; bottom: 20px; right: 20px;">
    <a href="#" style="text-decoration: none; color: #666;">
        <div style="background-color: #f8f9fa; padding: 10px 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            ↑ К содержанию
        </div>
    </a>
</div>
""", unsafe_allow_html=True)