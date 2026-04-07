# # # ---------------- BASE IMAGE ---------------- #
# # FROM python:3.12-slim

# # # ---------------- WORKDIR ---------------- #
# # WORKDIR /app

# # # ---------------- COPY PROJECT FILES ---------------- #
# # # Copy entire src folder into container
# # COPY .. /app

# # # ---------------- INSTALL DEPENDENCIES ---------------- #
# # RUN pip install --upgrade pip

# # # Install dependencies directly (since requirements.txt may not be final yet)
# # RUN pip install fastapi uvicorn scikit-learn xgboost joblib pandas numpy matplotlib seaborn

# # # ---------------- EXPOSE PORT ---------------- #
# # EXPOSE 8000

# # # ---------------- START SERVER ---------------- #
# # CMD ["uvicorn", "deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]




# # ---------------- BASE IMAGE ---------------- #
# FROM python:3.12-slim

# # Prevent python from writing pyc files
# ENV PYTHONDONTWRITEBYTECODE=1

# # Prevent python from buffering stdout
# ENV PYTHONUNBUFFERED=1

# # ---------------- WORKDIR ---------------- #
# WORKDIR /app

# # ---------------- COPY REQUIREMENTS FIRST ---------------- #
# COPY requirements.txt .

# # ---------------- INSTALL DEPENDENCIES ---------------- #
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# # ---------------- COPY PROJECT FILES ---------------- #
# COPY src /app

# # ---------------- EXPOSE PORT ---------------- #
# EXPOSE 8000

# # ---------------- START SERVER ---------------- #
# CMD ["uvicorn", "deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]



FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set PYTHONPATH so 'import src' works from anywhere
ENV PYTHONPATH=/app

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ /app/src/

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "src.deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]