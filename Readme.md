# Tilt case about electricity breakdown estimation

- Pre-requisites :
- Have Git install, Python3, Docker

Pull the repository and create a python development environment.
Go to app directory and install python dependencies with
```python
pip install -r requirements.txt
```
Than launch the app with

```python
streamlit run app.py
```

If Streamlit is not working on you machine, you can Dockerize the app. From the root directory :
```bash
docker build -t app .
```

Then you can launch it with :
```bash
docker run app -p 8080:8501 app:latest
```

Open you browser to [localhost:8080](localhost:8080)