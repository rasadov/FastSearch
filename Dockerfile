FROM python:3.11.2

# Set the working directory
WORKDIR /src

# Copy the current directory 

COPY requirements.txt /src

# Install the dependencies

RUN pip install --no-cache-dir -r requirements.txt

COPY . /src

ENV PYTHONPATH=/src

ENTRYPOINT [ "gunicorn" ]

CMD ["--workers=2", "src.app.__main__:app", "--bind=0.0.0.0:5000"]
