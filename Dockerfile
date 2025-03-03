FROM python:3.9


WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

#COPY <source> <destination>
COPY . .

#uvicorn app.main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

