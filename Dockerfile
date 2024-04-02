FROM python:3.11.2

# Set the working directory
WORKDIR /src

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev


# Copy the current directory 

COPY . .

# Install the dependencies

RUN pip install -r requirements.txt

# Run the application

CMD ["python", "src/app"]