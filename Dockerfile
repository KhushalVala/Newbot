# Microsoft ka official Playwright server jisme saari libraries pehle se hain
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app
COPY . /app

# Tere packages install karega
RUN pip install -r requirements.txt

# Tera bot chalu karega
CMD ["python", "bot.py"]
