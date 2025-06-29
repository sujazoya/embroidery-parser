FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN chmod +x render_build.sh
RUN ./render_build.sh

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "app:app"]
