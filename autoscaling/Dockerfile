FROM docker:27-cli AS dockercli
FROM python:3.10-slim

COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins /usr/local/libexec/docker/cli-plugins

WORKDIR /app
RUN pip install --no-cache-dir requests flask
COPY . /app
ENV PYTHONPATH=/app
EXPOSE 9090
CMD ["python", "-m", "autoscaling"]
