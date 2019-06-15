# flask-postits
📝 Just leave a note on the fridge

## Building
Clone the repository:

```
git clone https://github.com/khannurien/flask-postits
```
Build the Docker image:

```
cd flask-postits
docker build -t flask-postits .
```

## Running
Run a container:

```
docker run -p 5000:8000 flask-postits
```

Your fridge should be available at http://127.0.0.1:5000 🎉

Default login is `frigo` / `password`.
