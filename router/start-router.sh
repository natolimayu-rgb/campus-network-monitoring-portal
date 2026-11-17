
#!/bin/sh


iptables -P FORWARD DROP
iptables -F FORWARD
iptables -t nat -F POSTROUTING

iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

iptables -A FORWARD \
  -s 10.10.1.0/24 \
  -d 10.10.3.20 \
  -p tcp --dport 6379 \
  -j DROP

iptables -A FORWARD \
  -s 10.10.1.0/24 \
  -d 10.10.2.10 \
  -p tcp --dport 8000 \
  -j ACCEPT

iptables -A FORWARD \
  -s 10.10.2.10 \
  -d 10.10.3.20 \
  -p tcp --dport 6379 \
  -j ACCEPT

iptables -t nat -A POSTROUTING \
  -s 10.10.1.0/24 \
  -d 10.10.2.10 \
  -o eth0 \
  -j MASQUERADE

exec sleep infinity
