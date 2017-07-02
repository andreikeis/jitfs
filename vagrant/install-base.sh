#!/bin/bash -e

chmod 755 /home/vagrant

yum -y install epel-release
yum -y install python34
yum -y install python34-devel
yum -y install python-pip
yum -y install python-wheel
yum -y install git
yum -y install wget
yum -y install gcc-c++
yum -y install ninja-build
