FROM python:3.10.16-alpine

WORKDIR /home/

COPY ./requirements.txt /home/

# COPY ./app /home/app
RUN pip install -r requirements.txt
RUN mkdir app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]