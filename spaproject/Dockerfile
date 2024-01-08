# Используйте официальный образ Python с вашей версией Python
FROM python:3.10

# Установите рабочую директорию в контейнере
WORKDIR /app

# Установите переменные окружения, необходимые для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установите зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install python-magic
RUN pip install -r requirements.txt


# Копируйте проект
COPY . .

# Запустите команду для запуска вашего приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
