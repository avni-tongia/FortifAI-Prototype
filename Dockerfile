
FROM python:3.9-slim

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app

COPY . .

RUN pip install streamlit torch torchvision sentence-transformers scikit-learn pillow numpy

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
