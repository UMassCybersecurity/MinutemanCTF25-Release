FROM debian:bookworm-slim 

# Install Python
RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy ynetd and the Python script into the container

COPY . . 

# Make ynetd and the script executable
RUN chmod +x ynetd oooverflow1 

# Expose the port that ynetd will listen on
EXPOSE 19467 

# Start ynetd to serve the Python script
CMD ["./ynetd", "-p", "19467", "./oooverflow1"]

