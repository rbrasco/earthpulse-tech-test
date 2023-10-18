# Use an official GDAL runtime as a parent image
FROM ghcr.io/osgeo/gdal:ubuntu-small-latest 

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY ./src/. /app

# Install any needed packages for the base image
RUN apt-get update && apt-get install -y python3-pip 

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for uvicorn
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--reload"]
