#!/bin/bash

yum -y install wget tar gcc automake autoconf libtool make

# install epel, `luarocks` need it.
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
rpm -ivh epel-release-latest-7.noarch.rpm

# install etcd
wget https://github.com/etcd-io/etcd/releases/download/v3.4.13/etcd-v3.4.13-linux-amd64.tar.gz
tar -xvf etcd-v3.4.13-linux-amd64.tar.gz && \
    cd etcd-v3.4.13-linux-amd64 && \
    cp -a etcd etcdctl /usr/bin/

# add OpenResty source
yum install yum-utils
yum-config-manager --add-repo https://openresty.org/package/centos/openresty.repo

# install OpenResty and some compilation tools
yum install -y openresty curl git gcc luarocks lua-devel

# start etcd server
etcd &