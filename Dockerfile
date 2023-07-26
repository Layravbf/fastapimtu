FROM rabbitmq:3.8
EXPOSE 4369 5671 5672 25672
# RUN rabbitmq-plugins enable --offline rabbitmq_management
CMD ["rabbitmq-server"]


# Use the official Python base image with the desired version
FROM python:3.9
# Set the working directory inside the container
WORKDIR /app
# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Copy the source code into the container
COPY . .
# Expose the port that the FastAPI app will listen on
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
# Set the command to run your FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]