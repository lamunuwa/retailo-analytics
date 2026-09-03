FROM python:3.12-slim

WORKDIR /vision

RUN apt-get update \
    && apt-get install --no-install-recommends -y libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY vision/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY vision/ .

RUN adduser --disabled-password --gecos "" visionuser

RUN chown -R visionuser:visionuser /vision

USER visionuser

CMD ["python", "-m", "vision.src.main"]
