FROM python:3.11.2

# Set the working directory
WORKDIR /src

# Copy the current directory 

COPY . .

# Install the dependencies

RUN pip install -r requirements.txt

# Run the application

CMD ["python", "src/app"]