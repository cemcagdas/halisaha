FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0
ENV RESOLUTION=1520x950

# Gerekli sistem, sanal ekran ve VNC araçlarını yükle
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
    fonts-dejavu \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Python paketlerini kur
RUN pip3 install --no-cache-dir --break-system-packages customtkinter pillow

WORKDIR /app

# Proje dosyalarını içeri al
COPY . /app

# noVNC web arayüzünü hazırla ve index olarak ayarla
RUN cp /usr/share/novnc/vnc.html /usr/share/novnc/index.html 2>/dev/null || true

# Başlatma scriptini oluştur
RUN echo '#!/bin/bash\n\
Xvfb :0 -screen 0 ${RESOLUTION}x24 &\n\
sleep 1\n\
fluxbox &\n\
x11vnc -display :0 -nopw -listen 127.0.0.1 -forever -shared &\n\
websockify --web /usr/share/novnc 8501 127.0.0.1:5900 &\n\
python3 app.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8501

CMD ["/app/entrypoint.sh"]
