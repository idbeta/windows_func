FROM centos:7
ARG APISIX_VERSION=2.0
LABEL apisix_version="${APISIX_VERSION}"
RUN yum -y install wget tar gcc automake autoconf libtool make
RUN wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN rpm -ivh epel-release-latest-7.noarch.rpm
RUN wget https://github.com/etcd-io/etcd/releases/download/v3.4.13/etcd-v3.4.13-linux-amd64.tar.gz
RUN tar -xvf etcd-v3.4.13-linux-amd64.tar.gz && cd etcd-v3.4.13-linux-amd64 && cp -a etcd etcdctl /usr/bin/
RUN yum install yum-utils
RUN yum-config-manager --add-repo https://openresty.org/package/centos/openresty.repo
RUN yum install -y openresty curl git gcc luarocks lua-devel which
RUN etcd &
ENV PATH=$PATH:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin
RUN mkdir apisix-$APISIX_VERSION
WORKDIR apisix-$APISIX_VERSION
RUN wget https://downloads.apache.org/apisix/$APISIX_VERSION/apache-apisix-$APISIX_VERSION-src.tgz
RUN tar zxvf apache-apisix-$APISIX_VERSION-src.tgz
RUN make deps
EXPOSE 9080 9443
CMD ["/bin/sh", "-c", "./bin/apisix start"]
