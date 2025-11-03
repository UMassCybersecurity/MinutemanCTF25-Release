FROM python:latest
RUN apt-get update && apt-get install socat -y
WORKDIR /app
COPY chall.py you_dont_have_this_file.py ./
RUN chmod +x chall.py
ENV LISTEN_PORT=40447
CMD ["sh","-c","socat TCP-LISTEN:${LISTEN_PORT},reuseaddr,fork EXEC:'python3 chall.py',pty,stderr"]
