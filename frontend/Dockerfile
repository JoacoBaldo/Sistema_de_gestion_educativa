FROM python:3.11-slim

WORKDIR /app


RUN pip install --no-cache-dir Flask requests Jinja2

COPY . .

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Comando para correr el frontend en el puerto 5001
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]