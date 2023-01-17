docker build -t app .

docker run -p 8080:8501 \
    --mount type=bind,source="$(pwd)/app/",target=/app \
    app:latest

gcloud builds submit --tag gcr.io/imagerecodev/tilt-case --project imagerecodev