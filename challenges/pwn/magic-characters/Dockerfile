FROM ubuntu:24.04 AS challenge

RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install socat libc6:i386 -y

WORKDIR /ctf

COPY static/charcon . 
COPY flag.txt .

RUN chmod +x charcon
CMD ["sh", "-c", "socat TCP-LISTEN:${LISTEN_PORT},reuseaddr,fork EXEC:'./charcon',pty,stderr"]
