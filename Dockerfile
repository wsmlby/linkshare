FROM python:3.12-slim
WORKDIR /app
COPY linkshare.py .
EXPOSE 8000
CMD ["python", "-u", "linkshare.py", "serve"]