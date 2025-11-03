FROM python:3.14-slim

RUN apt-get update
RUN apt-get install -y python3-pip git

WORKDIR /app

RUN git clone https://github.com/NathanY3G/rp2040-pio-emulator.git
RUN pip3 install ./rp2040-pio-emulator
RUN pip3 install flask adafruit-circuitpython-pioasm gunicorn[standard]

COPY src ./src

WORKDIR /app/src

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "app:app" ]