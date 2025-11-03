FROM python:latest
RUN apt-get update && apt-get install socat -y

WORKDIR /app

COPY powerpuff.py ./

RUN chmod +x powerpuff.py
ENV LISTEN_PORT=40444

CMD ["sh","-c","socat TCP-LISTEn:${LISTEN_PORT},reuseaddr,fork EXEC:'python3 powerpuff.py',pty,stderr"]
