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

## Get working CentOS6 repositories

### Disable base, updates, extras, centosplus, contrib repositories:

```sh
# sed -i '/enabled=.*$/d;' /etc/yum.repos.d/CentOS-Base.repo
# sed -i 's/gpgcheck=1/gpgcheck=1\nenabled=0/g' /etc/yum.repos.d/CentOS-Base.repo
```

### CentOS 6.10 Vault repositories:

- get the repositories config file
```sh
# curl -o /etc/yum.repos.d/centos6-vault.repo https://repo.almalinux.org/elevate/el6/centos6-vault.repo
```

- or create the repository config manually
```sh
# cat > /etc/yum.repos.d/CentOS6.10-Vault.repo
[C6.10-base]
name=CentOS-6.10 - Base
baseurl=http://vault.centos.org/6.10/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
enabled=1

[C6.10-updates]
name=CentOS-6.10 - Updates
baseurl=http://vault.centos.org/6.10/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
enabled=1

[C6.10-extras]
name=CentOS-6.10 - Extras
baseurl=http://vault.centos.org/6.10/extras/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
enabled=1

[C6.10-contrib]
name=CentOS-6.10 - Contrib
baseurl=http://vault.centos.org/6.10/contrib/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
enabled=0
```

## Upgrade to *CentOS Linux release 7.2*

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

- add CentOS6 upgrade repository by installing package with the configuration file

```sh
# yum install https://repo.almalinux.org/elevate/el6/x86_64/elevate-release-1.0-2.el6.noarch.rpm
```

 - or download the repository configuration file
```sh
# curl -o /etc/yum.repos.d/ELevate.repo https://repo.almalinux.org/elevate/el6/elevate.repo
```

- or create the repository configuration file
```sh
# vi /etc/yum.repos.d/ELevate.repo
[elevate]
name=ELevate
baseurl=https://repo.almalinux.org/elevate/el6/$basearch/
gpgcheck=1
enabled=0
# disabled by redhat-upgrade-tool
priority=90
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-ELevate

## Sources
[elevate-source]
name=name=ELevate - Source
baseurl=https://repo.almalinux.org/elevate/el6/SRPMS/
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-ELevate
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

### How to mitigate of some risks and solve possible issues

#### Check list of risks

```sh
# preupg --riskcheck --verbose
```

#### Risk for: *GNOME desktop environment*

```log
preupg.risk.EXTREME: You have the GNOME desktop environment session as an option in your X11 session manager. The GNOME desktop environment as a part of the 'Desktop' yum group underwent a serious redesign in its user interface as well as in underlying technologies in CentOS 7.
```

The issue can be solved with removing `gnome-session-xsession` package.
```sh
# yum remove gnome-session-xsession
```
Please remember to restore all removed packages on new CentOS7 system after the migration.

#### Issue: Preserve `eth*` names for Network Interfaces (if applicable).

Edit the `/boot/grub/grub.conf` default boot entry, and append existing kernel options with `biosdevname=0 net.ifnames=0`, like:

```grub
kernel /vmlinuz-2.6.32-754.35.1.el6.x86_64 ... rhgb quiet biosdevname=0 net.ifnames=0
```

### Import CentOS 7 GPG key

CentOS7 repositories will be used to upgrade. So will need to import correct GPG key:

```sh
# rpm --import http://mirror.centos.org/centos/7/os/x86_64/RPM-GPG-KEY-CentOS-7
```

### Init the upgrade

> The `redhat-upgrade-tool` version *0.8.0* allows to upgrade to *CentOS release 7.2.1511*. The newer CentOS7 versions doesn't provide need data in the `.treeinfo` file, both at [repositories](https://vault.centos.org/7.2.1511/os/x86_64/.treeinfo) and on installation medias. The whole `checksums` part and `upgrade` parameter in `images-x86_64` part are missed.

```sh
redhat-upgrade-tool --network=7 --cleanup-post --instrepo=http://vault.centos.org/7.2.1511/os/x86_64/
```

 - `--cleanup-post` option will do CentOS 6 packages removal if any are still remain installed (had no update candidate).
 - `--network=RELEASEVER` Use online repos. `RELEASEVER` will be used to replace `$releasever` variable in any occur of repo URL.

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

- remove CentOS6 upgrade repository package:
```sh
# yum remove elevate-release
```
- or delete the CentOS6 upgrade repository config
```sh
# rm /etc/yum.repos.d/ELevate.repo
```
- remove CentOS Vault repository config:
```sh
# rm /etc/yum.repos.d/centos6-vault.repo
```

#### Put back CentOS7 repository:

```sh
# rpm -qV centos-release
S.5....T.  c /etc/yum.repos.d/CentOS-Base.repo
# mv /etc/yum.repos.d/CentOS-Base.repo.rpmnew /etc/yum.repos.d/CentOS-Base.repo
```

## Upgrade to *CentOS Linux release 7.9*

### Update whole system with yum

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