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

Run a container:

```
docker run -p 5000:8000 flask-postits
```
