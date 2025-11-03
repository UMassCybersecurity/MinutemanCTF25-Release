FROM python:latest 

# Install Python
# RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN apt-get install socat -y
RUN pip install pycryptodome

# Set working directory
WORKDIR /app

# Copy ynetd and the Python script into the container
COPY chall.py you_dont_have_this_file.py ./

# Make ynetd and the script executable
RUN chmod +x chall.py you_dont_have_this_file.py
ENV LISTEN_PORT=40445
CMD ["sh", "-c", "socat TCP-LISTEN:${LISTEN_PORT},reuseaddr,fork EXEC:'python3 chall.py',pty,stderr"]
