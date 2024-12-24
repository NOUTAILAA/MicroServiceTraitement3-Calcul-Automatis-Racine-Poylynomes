# Utilisation d'une image légère de Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source de l'application
COPY . .

# Exposer le port 5004 pour Flask
EXPOSE 5004

# Lancer l'application
CMD ["python", "app5.py"]
