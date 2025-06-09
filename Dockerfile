FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3.11 python3.11-venv python3-pip git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip
RUN pip install flask==2.3.2
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio && \
    pip install transformers numpy tqdm && \
    pip install -r requirements.txt
EXPOSE 8080
CMD ["./run_wina_ui.sh"]
