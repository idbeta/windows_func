FROM centos:7
RUN yum install -y git cmake gcc make \
    openssl-devel libssh2-devel openssh-server \
    git-daemon java-1.8.0-openjdk-headless
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]