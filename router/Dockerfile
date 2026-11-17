FROM alpine:3.22

RUN apk add --no-cache \
    iproute2 \
    iptables \
    iputils \
    tcpdump

COPY start-router.sh /start-router.sh

RUN chmod +x /start-router.sh

CMD ["sh", "/start-router.sh"]

