%global version_boom 0.8
%global boom_dir boom-%{version_boom}

Name:           redhat-upgrade-tool
Version:        0.8.0
Release:        2%{?dist}
Summary:        The CentOS Linux Upgrade tool
Epoch:          1

License:        GPLv2+
URL:            https://github.com/upgrades-migrations/redhat-upgrade-tool
Source0:        %{url}/archive/%{name}-%{version}.tar.gz
Source1:        boom-%{version_boom}.tar.gz
Patch1:         1-redhat-upgrade-tool-no-variants.patch
Patch2:         2-redhat-upgrade-tool-remove-rhsm-downloads.patch

Requires:       dbus
Requires:       grubby
Requires:       python-argparse
Requires:       preupgrade-assistant >= 2.2.0-1

# https://bugzilla.redhat.com/show_bug.cgi?id=1038299
Requires:       yum >= 3.2.29-43

BuildRequires:  python-libs
BuildRequires:  python2-devel
BuildRequires:  python-sphinx
BuildRequires:  python-setuptools

BuildArch:      noarch

# GET THEE BEHIND ME, SATAN
Obsoletes:      preupgrade

%description
redhat-upgrade-tool is the CentOS Linux Upgrade tool.



%prep
%setup -q -n %{name}-%{version}
%setup -q -T -D -a 1 -n %{name}-%{version}
%patch1 -p0
%patch2 -p0

%build
make PYTHON=%{__python}

###### boom #######
pushd %{boom_dir}
CFLAGS="%{optflags}"
%{__python} setup.py %{?py_setup_args} build --executable="%{__python} -s"
popd


%install
rm -rf $RPM_BUILD_ROOT
make install PYTHON=%{__python} DESTDIR=$RPM_BUILD_ROOT MANDIR=%{_mandir}
# backwards compatibility symlinks, wheee
ln -sf redhat-upgrade-tool $RPM_BUILD_ROOT/%{_bindir}/redhat-upgrade-tool-cli
ln -sf redhat-upgrade-tool.8 $RPM_BUILD_ROOT/%{_mandir}/man8/redhat-upgrade-tool-cli.8
# updates dir
mkdir -p $RPM_BUILD_ROOT/etc/redhat-upgrade-tool/update.img.d

###### boom #######
pushd %{boom_dir}
%{__python} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}

# Install Grub2 integration scripts
mkdir -p ${RPM_BUILD_ROOT}/etc/grub.d
mkdir -p ${RPM_BUILD_ROOT}/etc/default
install -m 755 etc/grub.d/42_boom ${RPM_BUILD_ROOT}/etc/grub.d
install -m 644 etc/default/boom ${RPM_BUILD_ROOT}/etc/default

# Make configuration directories
# NOTE: think about remove of examples completely..
mkdir -p ${RPM_BUILD_ROOT}/boot/boom/profiles
mkdir -p ${RPM_BUILD_ROOT}/boot/loader/entries
install -d -m 750 ${RPM_BUILD_ROOT}/boot/boom/profiles ${RPM_BUILD_ROOT}
install -d -m 750 ${RPM_BUILD_ROOT}/boot/loader/entries ${RPM_BUILD_ROOT}
install -m 644 examples/profiles/*.profile ${RPM_BUILD_ROOT}/boot/boom/profiles
install -m 644 examples/boom.conf ${RPM_BUILD_ROOT}/boot/boom

# Automatically enable legacy bootloader support for RHEL6 builds
sed -i 's/enable = False/enable = True/' ${RPM_BUILD_ROOT}/boot/boom/boom.conf

popd

# Move the boom utility under libexec as it is not supposed to be used by
# users directly
mv ${RPM_BUILD_ROOT}/%{_bindir}/boom ${RPM_BUILD_ROOT}/%{_libexecdir}/boom

%post
if [ ! -e /var/lib/dbus/machine-id ]; then
    dbus-uuidgen > /var/lib/dbus/machine-id
fi

# CentOS branding
ln -sf redhat-upgrade-tool $RPM_BUILD_ROOT/%{_bindir}/centos-upgrade-tool
ln -sf centos-upgrade-tool $RPM_BUILD_ROOT/%{_bindir}/centos-upgrade-tool-cli
ln -sf redhat-upgrade-tool.8 $RPM_BUILD_ROOT/%{_mandir}/man8/centos-upgrade-tool.8
ln -sf centos-upgrade-tool.8 $RPM_BUILD_ROOT/%{_mandir}/man8/centos-upgrade-tool-cli.8

%files
%{!?_licensedir:%global license %%doc}
%doc README.asciidoc COPYING

# boom doc files
%license %{boom_dir}/COPYING
%doc %{boom_dir}/README.md
%if 0%{?sphinx_docs}
%doc doc/html/
%endif # if sphinx_docs
%doc %{boom_dir}/examples/*

# systemd stuff
%if 0%{?_unitdir:1}
%{_unitdir}/system-upgrade.target
%{_unitdir}/upgrade-prep.service
%{_unitdir}/upgrade-switch-root.service
%{_unitdir}/upgrade-switch-root.target
%endif
# upgrade prep program
%{_libexecdir}/upgrade-prep.sh
# SysV init replacement
%{_libexecdir}/upgrade-init
# python library
%{python_sitelib}/redhat_upgrade_tool*
# binaries
%{_bindir}/redhat-upgrade-tool
%{_bindir}/redhat-upgrade-tool-cli
# man pages
%{_mandir}/man*/*
# empty config dir
%dir /etc/redhat-upgrade-tool
# empty updates dir
%dir /etc/redhat-upgrade-tool/update.img.d

# boom
%{python_sitelib}/boom*
%{_libexecdir}/boom
/etc/grub.d/42_boom
%config(noreplace) /etc/default/boom
%config(noreplace) /boot/boom/boom.conf
/boot/*

%changelog
* Tue Apr 2 2024 Yuriy Kohut <ykohut@almalinux.org> - 1:0.8.0-2
- Add CentOS branding with patches: 1-redhat-upgrade-tool-no-variants.patch, 2-redhat-upgrade-tool-remove-rhsm-downloads.patch

* Thu Sep 06 2018 Petr Stodulka <pstodulk@redhat.com> - 1:0.8.0-1
- Add the rollback capability
  Resolves: rhbz#1625999

* Tue Jun 12 2018 Michal Bocek <mbocek@redhat.com> - 1:0.7.52-1
- Add option to disable /boot size check
  Resolves: rhbz#1518317

* Mon Nov 08 2017 Michal Bocek <mbocek@redhat.com> - 1:0.7.51-1
- Remove dependency on preupgrade-assistant-el6toel7 package
- Fail with proper error message when .treeinfo is not available
  Related: rhbz#1486439
- Check if upgrading to the RHEL version allowed by the Preupgrade Assistant
  Resolves: rhbz#1436310

* Mon Sep 25 2017 Michal Bocek <mbocek@redhat.com> - 1:0.7.50-1
- Decompress kernel modules (applies to RHEL 7.4+)
  Resolves: rhbz#1486962
- Add rpm dependency of preupgrade-assistant-el6toel7

* Fri Jun 16 2017 Michal Bocek <mbocek@redhat.com> - 1:0.7.49-1
- Check for sufficient space in /boot
  Resolves: rhbz#1361219
- Downloading treeinfo if .treeinfo not in repo
  Resolves: rhbz#1410949
- Support for new treeinfo format of RHEL 7.4 repos
  Resolves: rhbz#1456809

* Mon Dec 5 2016 Michal Bocek <mbocek@redhat.com> - 1:0.7.48-1
- Support Preupgrade Assistant version 2.2.0
  Resolves: rhbz#1398401
- Fix usage of HTTPS repo URL with --noverify option
  Resolves: rhbz#1398318

* Thu Oct 6 2016 Michal Bocek <mbocek@redhat.com> - 1:0.7.47-1
- Fix traceback caused by Unicode characters that appear in raw_input
  prompt message during the import of GPG keys.
  Related: rhbz#1150029

* Wed Sep 7 2016 Michal Bocek <mbocek@redhat.com> - 1:0.7.46-1
- Reverted changes from 0.7.45 regarding "New return codes from
  preupgrade-assistant."
  Related: rhbz#1371553

* Tue Aug 30 2016 Michal Bocek <mbocek@redhat.com> - 1:0.7.45-1
- New return codes from preupgrade-assistant.
  Resolves: rhbz#1371553
- Support include in .repo files.
  Resolves: rhbz#1270223
- Prompt user to accept GPG key import.
  Resolves: rhbz#1150029
- Fix PYCURL ERROR 22 - remove tool cache at the start of the tool.
  Resolves: rhbz#1303982

* Tue Jul 26 2016 Petr Hracek <phracek@redhat.com> - 1:0.7.44-2
- Correct dependency on preupgrade-assistant
  Related: rhbz#1356806

* Mon Jul 25 2016 Michal Bocek <mbocek@redhat.com> 0.7.44-1
- Fix tool failure due to AttributeError (check_inplace_risk).
  Resolves: rhbz#1356806

* Wed Oct 14 2015 David Shea <dshea@redhat.com> 0.7.43-1
- Fix the iteration over failed preupgrade scripts (mganisin)
  Related: rhbz#1252850

* Wed Sep  9 2015 David Shea <dshea@redhat.com> 0.7.42-1
- Run all preupgrade scripts and report which failed (phracek)
  Resolves: rhbz#1252850

* Fri Jul 10 2015 David Shea <dshea@redhat.com> 0.7.41-1
- Use the filename to determine the kernel version for new-kernel-pkg.
  Resolves: rhbz#1241875

* Wed Jul  1 2015 David Shea <dshea@redhat.com> 0.7.40-1
- Apply sslnoverify to all setup_downloader calls
  Related: rhbz#1169969

* Thu Jun 25 2015 David Shea <dshea@redhat.com> 0.7.39-1
- Fix traceback for transaction problems with one package
  Resolves: rhbz#1220291

* Wed Jun 24 2015 David Shea <dshea@redhat.com> 0.7.38-1
- Remove the KeyboardInterruptMessage
- Retry raw_input on SIGWINCH
  Resolves: rhbz#1106485
- Do not use losetup for the ISO file name
  Related: rhbz#1054048
- Fix logging in media.py
- Modify yum repo mountpoints before reboot.
  Resolves: rhbz#1225092

* Tue May 12 2015 David Shea <dshea@redhat.com> 0.7.37-1
- Convert bootloader arguments before upgrade (phracek)
  Resolves: rhbz#1081047

* Wed Apr  8 2015 David Shea <dshea@redhat.com> 0.7.36-1
- Add an option to disable SSL certificate verification
  Resolves: rhbz#1169969
- Change the message shown when no upgrade is found.
  Resolves: rhbz#1199927

* Wed Apr  8 2015 David Shea <dshea@redhat.com> 0.7.35-1
- Handle EOFError in raw_input
  Resolves: rhbz#1106485
- Check proper upgrade target version (phracek)
  Resolves: rhbz#1199087
- Add a message on check_release_version_file failures
  Related: rhbz#1199087

* Fri Feb 13 2015 David Shea <dshea@redhat.com> 0.7.34-1
- Run setup_cleanup_post earlier (fkluknav)
  Related: rhbz#1187024

* Mon Feb  2 2015 David Shea <dshea@redhat.com> 0.7.33-1
- Write all command-line options to upgrade.conf (fkluknav)
  Resolves: rhbz#1187024

* Fri Sep 19 2014 David Shea <dshea@redhat.com> 0.7.32-1
- Fix the URLGrabError import
  Related: rhbz#1076120

* Fri Sep 19 2014 David Shea <dshea@redhat.com> 0.7.31-1
- Fix ValueError with --addrepo/--repo REPOID (wwoods)
  Related: rhbz#1084985
- Add a message about invalid repo URLs
  Resolves: rhbz#1084985
- Catch exceptions from early treeinfo parsing
  Resolves: (#1076120)

* Wed Sep 17 2014 David Shea <dshea@redhat.com> 0.7.30-1
- Fix the enabled line on disabled yum repos
  Related: rhbz#1130686

* Fri Sep 12 2014 David Shea <dshea@redhat.com> 0.7.29-1
- Disable yum repos with no enabled= line
  Resolves: rhbz#1130686

* Mon Sep  8 2014 David Shea <dshea@redhat.com> 0.7.28-1
- Execute preupgrade-scripts after storing RHEL-7 repos (phracek)
  Related: rhbz#1138615

* Mon Sep  8 2014 David Shea <dshea@redhat.com> 0.7.27-1
- Fix fedup.util.rlistdir
  Related: rhbz#1138615
- Run preupgrade scripts before setting up the upgrade
  Resolves: rhbz#1138615

* Fri Aug 15 2014 David Shea <dshea@redhat.com> 0.7.26-1
- Fix the search for enabled repos to disable.
  Related: rhbz#1075486

* Mon Aug  4 2014 David Shea <dshea@redhat.com> 0.7.25-1
- Add --instrepokey (wwoods)
  Related: rhbz#1115532
  Related: rhbz#1123915
- Automatically add the GPG key to Red Hat repos.
  Resolves: rhbz#1123915
- Revert "fetch/verify .treeinfo.signed if gpgcheck is on"
  Related: rhbz#1123915
- Cleanup repo files added by redhat-upgrade-tool
- Fix a crash if cleaning up without /var/lib/system-upgrade
- Write GPG information to the yum repo files
  Resolves: rhbz#1115532

* Tue Jul  1 2014 David Shea <dshea@redhat.com> 0.7.24-1
- Upgrade repos are enabled by default (phracek)
- Always disable old repos
- Disable repos from RHEL-6 before starting the upgrade.

* Wed Jun 25 2014 David Shea <dshea@redhat.com> 0.7.23-1
- Skip unavailable repos during the postupgrade scripts
  Resolves: rhbz#1106401

* Wed Jun  4 2014 David Shea <dshea@redhat.com> 0.7.22-1
- Use the mkdir_p wrapper instead of os.makedirs
  Resolves: rhbz#1104780

* Tue Jun  3 2014 David Shea <dshea@redhat.com> 0.7.21-1
- Workaround .pem being removed by redhat-upgrade-tool --clean (jdornak)
  Related: rhbz#1071902
- Always create the upgrade.conf directory
  Related: rhbz#1070603
- Copy upgrade.conf to /root/preupgrade
  Related: rhbz#1070603
- Revert "Don't cleanup upgrade.conf for now"
  Related: rhbz#1070603

* Mon Jun  2 2014 David Shea <dshea@redhat.com> 0.7.20-1
- Add net.ifnames=0 to the boot command line
  Resolves: rhbz#1089212

* Thu May 29 2014 David Shea <dshea@redhat.com> 0.7.19-1
- Download RHSM product certificates (jdornak)
  Resolves: rhbz#1071902
- Workaround: Install RHSM product certificates in case that redhat-upgrade-dracut have not installed them. (jdornak)
  Resolves: rhbz#1071902

* Fri May 23 2014 David Shea <dshea@redhat.com> 0.7.18-1
- Fix the arg used with --device (bmr)
  Related: rhbz#1083169

* Fri May 23 2014 David Shea <dshea@redhat.com> 0.7.17-1
- Attempt to bring the network up during upgrade-init
  Resolves: rhbz#1089212

* Thu May 22 2014 David Shea <dshea@redhat.com> 0.7.16-1
- Run realpath on --device arguments.
  Resolves: rhbz#1083169

* Thu May 22 2014 David Shea <dshea@redhat.com> 0.7.15-1
- Add an option --cleanup-post to cleanup packages in post scripts.
  Resolves: rhbz#1070603
- Add a Requires for a sufficiently new yum
  Resolves: rhbz#1084165
- Disable screen blanking
  Resolves: rhbz#1070112
- Clear upgrade.conf before starting
  Related: rhbz#1100391
- Don't cleanup upgrade.conf for now
  Related: rhbz#1100391

* Tue May 20 2014 David Shea <dshea@redhat.com> 0.7.14-1
- Move the repo files to /etc/yum.repos.d
  Related: rhbz#1080966

* Thu May  8 2014 David Shea <dshea@redhat.com> 0.7.13-1
- Move system-upgrade.target.requires mounts into a shell script
  Resolves: rhbz#1094193

* Fri May  2 2014 David Shea <dshea@redhat.com> 0.7.12-1
- Added a check to prevent cross-variant upgrades.
  Resolves: rhbz#1070114

* Fri Apr 11 2014 David Shea <dshea@redhat.com> 0.7.11-1
- Save the repo config files to /var/tmp/system-upgrade/yum.repos.d
  Resolves: rhbz#1080966

* Thu Apr  3 2014 David Shea <dshea@redhat.com> 0.7.10-1
- Revise how preupgrade issues are printed
  Related: rhbz#1059447
- Call preupgrade-assistant API directly (phracek)
  Related: rhbz#1059447

* Thu Apr  3 2014 David Shea <dshea@redhat.com> 0.7.9-1
- Disable plymouth to workaround not reaching sysinit.target
  Resolves: rhbz#1060789
- Handle missing version arguments
  Resolves: rhbz#1069836
- Require --instrepo with --network.
  Resolves: rhbz#1070080
- Fix the reboot command for RHEL 6.
  Resolves: rhbz#1070821

* Wed Mar  5 2014 David Shea <dshea@redhat.com> 0.7.8-1
- Remove the unused systemd requires.
  Related: rhbz#1059447
- Check for preupgrade-assistant risks
  Resolves: rhbz#1059447
- Don't display package problems covered by preupgrade-assistant
  Related: rhbz#1059447
- Revise the preupgrade HIGH risk message.
  Related: rhbz#1059447

* Wed Feb 26 2014 David Shea <dshea@redhat.com> 0.7.7-1
- Remove the output parameter from CalledProcessException
  Resolves: rhbz#1054048

* Wed Feb 12 2014 David Shea <dshea@redhat.com> 0.7.6-1
- Add a generic problem summarizer.
  Resolves: rhbz#1040684
- Fix the dependency problem summary
  Related: rhbz#1040684

* Tue Jan 28 2014 David Shea <dshea@redhat.com> 0.7.5-1
- Replace subprocess backports with the versions from Python 2.7 (dshea)
  Resolves: rhbz#1054048
- Use the output of losetup to find the loop file (dshea)
  Related: rhbz#1054048
- Fix a misnamed variable in device_or_mnt (dshea)
  Related: rhbz#1054048
- fix UnboundLocalError with fedup --device (wwoods)
  Related: rhbz#1054048

* Mon Dec  2 2013 David Shea <dshea@redhat.com> 0.7.4-1
- Remove the URL from Source0
  Related: rhbz#1034906

* Tue Nov 26 2013 David Shea <dshea@redhat.com> 0.7.4-0
- Fix the kernel and initrd names. (#1031951)
- Remove rhgb quiet from the kernel command line. (#1032038)
- Remove the output parameter from CalledProcessError (#1032038)
- Change the python-devel BuildRequires to python-libs

* Tue Nov 19 2013 David Shea <dshea@redhat.com> 0.7.3-0
- Initial package for RHEL 6
  Resolves: rhbz#1012617
