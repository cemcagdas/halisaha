FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0
ENV RESOLUTION=1600x980

# Gerekli sanal ekran, ses ve web köprüsü paketlerini yükle
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    fonts-dejavu-core \
    fonts-segoe-ui-symbol \
    && rm -rf /var/lib/apt/lists/*

# Python kütüphanelerini kur
RUN pip3 install --no-cache-dir --break-system-packages customtkinter pillow

WORKDIR /app

# Proje dosyalarını kopyala
COPY . /app

# Başlatıcı script oluştur
RUN echo '#!/bin/bash\n\
Xvfb :0 -screen 0 ${RESOLUTION}x24 &\n\
sleep 1\n\
fluxbox &\n\
x11vnc -display :0 -nopw -listen localhost -xkb -ncache 10 -forever &\n\
websockify --web /usr/share/novnc 8501 localhost:5900 &\n\
python3 app.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8501

CMD ["/app/entrypoint.sh"]
