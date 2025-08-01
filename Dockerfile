FROM python:3.10

WORKDIR /backend

COPY ./backend/requirements.txt .

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
