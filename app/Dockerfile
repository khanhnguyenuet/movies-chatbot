FROM python:3.10.16-alpine

WORKDIR /home

COPY ./requirements.txt /home

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir app
# COPY ./app /home/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]