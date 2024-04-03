FROM python:3.11.6

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the main.py file directly 
COPY main.py .

# Copy the chess directory
COPY Chess Chess

# Copy the AI directory 
COPY AI AI

CMD ["python", "main.py"] 

