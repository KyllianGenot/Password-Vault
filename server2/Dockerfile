FROM python:3.9
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
