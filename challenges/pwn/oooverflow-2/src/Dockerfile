FROM python:latest

WORKDIR /ctf

COPY . .

RUN chmod +x oooverflow2 ynetd

EXPOSE 9123 

CMD ["./ynetd", "-p", "9123", "./oooverflow2"]

