FROM golang:1.23-bookworm
COPY . /src
WORKDIR /src
RUN go build -o /usr/local/bin/github-exporter
ENTRYPOINT /usr/local/bin/github-exporter
