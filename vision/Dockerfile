FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY vision/requirements.txt ./vision/requirements.txt
RUN pip install --no-cache-dir \
        torch==2.14.0+cpu torchvision==0.29.0+cpu \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r vision/requirements.txt

COPY vision/ ./vision/
COPY yolov8n.pt ./yolov8n.pt

RUN adduser --disabled-password --gecos "" visionuser

RUN chown -R visionuser:visionuser /app

USER visionuser

CMD ["python", "-m", "vision.src.main"]
