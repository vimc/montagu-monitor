FROM alpine:3.20
RUN apk add --no-cache openssl
WORKDIR /tls
COPY generate_cert.sh /generate_cert.sh
RUN chmod +x /generate_cert.sh
ENTRYPOINT ["/generate_cert.sh"]
