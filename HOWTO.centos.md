## Overview

`redhat-upgrade-tool` is the CentOS Linux Upgrade tool.
The tool is to upgrade *CentOS release 6.10* into CentOS *Linux release 7.2.1511* (*x86_64* only)

## The tool aliases

- `centos-upgrade-tool`
- `centos-upgrade-tool-cli`

## Upstream sources and preupgrade data

- [CentOS Upgrade Tool](https://github.com:upgrades-migrations/redhat-upgrade-tool.git)

- [A framework designed to run the Preupgrade Assistant modules](https://github.com:upgrades-migrations/preupgrade-assistant.git)

- [Modules used by upgrade from CentOS 6 to CentOS 7](https://github.com:upgrades-migrations/preupgrade-assistant-modules.git)

- [CentOS Preupgrade Data](https://git.centos.org/sources/preupgrade-assistant-el6toel7-data/c6/)

## Required packages to upgrade via command-line

```sh
preupgrade-assistant-2.6.2-2.el6.noarch.rpm
preupgrade-assistant-el6toel7-0.8.0-4.el6.noarch.rpm
preupgrade-assistant-el6toel7-data-0.20200704-2.el6.noarch.rpm
redhat-upgrade-tool-0.8.0-10.el6.noarch.rpm
```

Additional available packages:

```sh
preupgrade-assistant-tools-2.6.2-2.el6.noarch.rpm
preupgrade-assistant-ui-2.6.2-2.el6.noarch.rpm
```

## How to upgrade

### Make sure you are logged in as root user

```sh
# whoami
root
```

###  Update your system

It is assumed your system has got most recent CentOS6 packages:
```sh
# cat /etc/centos-release 
CentOS release 6.10 (Final)
```

### Add CentOS6 upgrade repository

 - download the repository configuration file
```sh
# curl -o /etc/yum.repos.d/elevate-c6.repo https://repo.almalinux.org/elevate/testing/elevate-c6.repo
```

- or create the repository configuration file
```sh
# vi /etc/yum.repos.d/elevate-c6.repo

[elevate-c6]
name=ELevate for CentOS6
baseurl=https://build.almalinux.org/pulp/content/copr/yuravk-elevate-c6-centos6-x86_64-dr/
gpgkey=https://repo.almalinux.org/elevate/RPM-GPG-KEY-ELevate

[elevate-c6-source]
name=name=ELevate for CentOS6 - Source
baseurl=https://build.almalinux.org/pulp/content/copr/yuravk-elevate-c6-centos6-src-dr/
enabled=0
gpgkey=https://repo.almalinux.org/elevate/RPM-GPG-KEY-ELevate
```

###  Install packages

```sh
# yum install redhat-upgrade-tool preupgrade-assistant-contents
```

That should install as minimum as the following packages:

```sh
Installing:
...
 preupgrade-assistant-el6toel7      noarch  0.8.0-4.el6
 redhat-upgrade-tool                noarch  1:0.8.0-10.el6
Installing for dependencies:
...
 preupgrade-assistant               noarch   2.6.2-2.el6
 preupgrade-assistant-el6toel7-data noarch   0.20200704-2.el6
 ...
 ```

### Run preupgrade assistant

It performs assessment of the system from the "upgradeability" point of view:

```sh
# preupg
```

### Inspect preupgrade status

Read carefully generated /root/preupgrade/result.html to get to know whether your system is “ready” to upgrade. The `lynx` example:

```sh
# lynx /root/preupgrade/result.html
```

### Import CentOS 7 GPG key

CentOS7 repositories will be used to upgrade. So will need to import correct GPG key:

```sh
# rpm --import http://mirror.centos.org/centos/7/os/x86_64/RPM-GPG-KEY-CentOS-7
```

### Init the upgrade

> The `centos-upgrade-tool-cli` version *0.8.0* allows to upgrade to *CentOS release 7.2.1511*. The newer CentOS7 versions doesn't provide need data in the `.treeinfo` file, both at [repositories](https://vault.centos.org/7.2.1511/os/x86_64/.treeinfo) and on installation medias. The whole `checksums` part and `upgrade` parameter in `images-x86_64` part are missed.

```sh
centos-upgrade-tool-cli --network=7 --force --cleanup-post --instrepo=http://vault.centos.org/7.2.1511/os/x86_64/
```
The `--force` option is to upgrade to CentOS 7.2 even current *Preupgrade Data* is for CentOS 7.9.

The `--cleanup-post` option will do CentOS 6 packages removal if any are still remain installed (had no update candidate).

### Reboot

Reboot your system as requested.

### During the boot

Boot loader will prompt to boot with `System Upgrade (redhat-upgrade-tool)`, please choose that option or wait for automatic boot.

The system will reboot twice during the upgrade.

### Post upgrade
Log into upgraded system (main console) and check its version:

```sh
# cat /etc/centos-release
CentOS Linux release 7.2.1511 (Core)
```

#### Disable CentOS6 repositories

If any, disable CentOS6 repositories. 

#### Put back CentOS7 repository:

```sh
# rpm -qV centos-release
S.5....T.  c /etc/yum.repos.d/CentOS-Base.repo
# mv /etc/yum.repos.d/CentOS-Base.repo.rpmnew /etc/yum.repos.d/CentOS-Base.repo
```

#### Get recent version

Update CentOS7 to the most recent version:
```sh
# yum update
```
Reboot when completed.

### Check your system

The system should be on 7.9.2009 version:
```sh
# cat /etc/centos-release
CentOS Linux release 7.9.2009 (Core)
```