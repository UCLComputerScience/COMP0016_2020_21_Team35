# Certified Asterisk 13.1-cert2 with sip and pjsip channels
FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

COPY scripts/build.sh /tmp/
COPY conf/asterisk-build/menuselect.makeopts /tmp/
COPY conf/fail2ban/filter.d/asterisk*.conf /tmp/
COPY conf/fail2ban/jail.conf /tmp/
COPY scripts/start.sh /

RUN /bin/sh /tmp/build.sh

COPY conf/asterisk-build/extensions.conf /etc/asterisk/
COPY conf/asterisk-build/pjsip.conf /etc/asterisk/
COPY conf/asterisk-build/modules.conf /etc/asterisk/
COPY conf/asterisk-build/manager.conf /etc/asterisk/
COPY conf/asterisk-build/agi-bin /var/lib/asterisk/agi-bin/
COPY conf/asterisk-build/voice /var/lib/asterisk/sounds/voice/

WORKDIR /root
CMD ["/bin/sh", "/start.sh"]
