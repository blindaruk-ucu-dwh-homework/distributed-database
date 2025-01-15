FROM python:3.9-slim

WORKDIR /app

# Копіюємо файли requirements.txt та ваш код
COPY requirements.txt .
COPY init.py .

COPY .. .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт
EXPOSE 5000

# Запускаємо сервер
CMD ["python", "init.py"]
