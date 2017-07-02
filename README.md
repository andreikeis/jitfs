# jitfs

## Vagrant setup

### Prerequisites
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/docs/installation/)
* Install the [Guest Additions plugin](https://github.com/dotless-de/vagrant-vbguest) for Vagrant
``` sh
vagrant plugin install vagrant-vbguest
```

```
cd vagrant
vagrant up --provision jitfs
vagrant ssh jitfs
```

Once inside vagrant, activate virtual environment:

```
```

