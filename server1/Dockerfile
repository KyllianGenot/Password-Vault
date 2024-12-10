FROM python:3.9
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
