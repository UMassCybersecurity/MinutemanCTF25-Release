FROM python:3.12

RUN useradd -ms /bin/bash newuser
USER newuser
RUN pip3 install flask
COPY ./src/ /src
WORKDIR "/src"
EXPOSE 8080
CMD ["python3", "./main.py"]