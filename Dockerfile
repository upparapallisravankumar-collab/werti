# ---------- Base Image ----------
FROM python:3.10-slim

# ---------- Set Working Directory ----------
WORKDIR /app

# ---------- Copy Files ----------
COPY . /app

# ---------- Install Dependencies ----------
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Expose Streamlit Port ----------
EXPOSE 8501

# ---------- Run Streamlit App ----------
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
