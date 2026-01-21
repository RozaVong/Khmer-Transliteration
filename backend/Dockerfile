FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/backend/logs
EXPOSE 8001
# Set Keras backend to TensorFlow and suppress TF warnings
ENV KERAS_BACKEND=tensorflow
ENV TF_CPP_MIN_LOG_LEVEL=2
CMD ["python", "main.py"]