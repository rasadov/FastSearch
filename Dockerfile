FROM python:3.11.2

# Set the working directory
WORKDIR /src

# Copy the current directory 

COPY requirements.txt /src

# Install the dependencies

RUN pip install --no-cache-dir -r requirements.txt

COPY . /src

# Run the application

CMD ["python", "src/app"]
