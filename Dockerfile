FROM --platform=linux/amd64 python:3.10.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the port number the container should expose
EXPOSE 5001

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port","5001" , "--theme.base", "light","--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
