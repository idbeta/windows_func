FROM centos:7
RUN sudo yum install -y openresty curl git gcc luarocks lua-devel
RUN wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN sudo rpm -ivh epel-release-latest-7.noarch.rpm
RUN wget https://github.com/etcd-io/etcd/releases/download/v3.4.13/etcd-v3.4.13-linux-amd64.tar.gz
RUN tar -xvf etcd-v3.4.13-linux-amd64.tar.gz && cd etcd-v3.4.13-linux-amd64 && sudo cp -a etcd etcdctl /usr/bin/
RUN etcd &
RUN mkdir apisix-2.0
RUN cd apisix-2.0
RUN wget https://downloads.apache.org/apisix/2.0/apache-apisix-2.0-src.tgz
RUN tar zxvf apache-apisix-2.0-src.tgz
RUN make deps
RUN ./bin/apisix start
EXPOSE 9080
