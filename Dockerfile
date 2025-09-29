FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]