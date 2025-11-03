FROM python:3.14-slim

RUN apt-get update
RUN apt-get install -y python3-pip git

WORKDIR /app

RUN pip3 install flask adafruit-circuitpython-pioasm gunicorn
RUN git clone https://github.com/omzz15/rp2040-pio-emulator.git
RUN pip3 install ./rp2040-pio-emulator

COPY src ./src

WORKDIR /app/src

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "--bind", "0.0.0.0:8000", "app:app"]
