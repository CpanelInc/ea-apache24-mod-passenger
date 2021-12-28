%global debug_package %{nil}

# Defining the package namespace
%global bundled_boost_version 1.60.0

%global passenger_libdir    %{_datadir}/passenger
%global passenger_archdir   %{_libdir}/passenger
%global passenger_agentsdir %{_libexecdir}/passenger

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define release_prefix 2

%global _httpd_mmn         %(cat %{_includedir}/apache2/.mmn 2>/dev/null || echo missing-ea-apache24-devel)
%global _httpd_confdir     %{_sysconfdir}/apache2/conf.d
%global _httpd_modconfdir  %{_sysconfdir}/apache2/conf.modules.d
%global _httpd_moddir      %{_libdir}/apache2/modules

%define ea_openssl_ver 1.1.1d-1
%define ea_libcurl_ver 7.68.0-2

Summary: Phusion Passenger application server
Name: ea-apache24-mod-passenger
Version: 6.0.10
Release: %{release_prefix}%{?dist}.cpanel
Group: System Environment/Daemons
# Passenger code uses MIT license.
# Bundled(Boost) uses Boost Software License
# BCrypt and Blowfish files use BSD license.
# Documentation is CC-BY-SA
# See: https://bugzilla.redhat.com/show_bug.cgi?id=470696#c146
License: Boost and BSD and BSD with advertising and MIT and zlib
URL: https://www.phusionpassenger.com

Source1: apache-passenger.conf.in
Source2: passenger_apps.default

BuildRequires: tree

BuildRequires: ea-apache24-devel
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: rubygem-rake
BuildRequires: rubygem-rake-compiler
BuildRequires: perl
BuildRequires: curl
BuildRequires: python3
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: ea-apr
BuildRequires: ea-apr-devel
BuildRequires: ea-apr-util
BuildRequires: ea-apr-util-devel

BuildRequires: ea-passenger-src

BuildRequires: ea-apache24-devel
%if 0%{?rhel} < 8
BuildRequires: ea-brotli
BuildRequires: ea-brotli-devel
BuildRequires: ea-libcurl >= %{ea_libcurl_ver}
BuildRequires: ea-libcurl-devel >= %{ea_libcurl_ver}
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11-devel >= %{ea_openssl_ver}
%else
BuildRequires: brotli
BuildRequires: brotli-devel
BuildRequires: libcurl
BuildRequires: libcurl-devel
BuildRequires: openssl
BuildRequires: openssl-devel
%endif

Requires: python3
Requires: ruby
Requires: ea-apr
Requires: ea-apr-util

%if 0%{?rhel} < 8
Requires: ea-brotli
Requires: ea-libcurl >= %{ea_libcurl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%else
Requires: brotli
Requires: libcurl
Requires: openssl
%endif

Provides: bundled(boost) = %{bundled_boost_version}

Provides: apache24-passenger
Conflicts: apache24-passenger

Requires: ea-passenger-runtime

%description
Phusion Passenger(r) is a web server and application server, designed to be fast,
robust and lightweight. It takes a lot of complexity out of deploying web apps,
adds powerful enterprise-grade features that are useful in production,
and makes administration much easier and less complex. It supports Ruby,
Python, Node.js and Meteor.

%package doc
Summary: Phusion Passenger documentation
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
License: CC-BY-SA and MIT and (MIT or GPL+)

%description doc
This package contains documentation files for Phusion Passenger(r).

%prep
set -x 
cp -rf /opt/cpanel/ea-passenger-src/passenger-*/ .

%build

set -x 

MYPWD=`pwd`
rm -rf %{buildroot}
mkdir -p %{buildroot}

cd passenger-release-%{version}

echo "RERAKE"

# rerun rake to make sure the code our patches applied and are used
rm -f src/apache2_module/ConfigGeneral/AutoGeneratedDefinitions.cpp
rm -f src/apache2_module/ConfigGeneral/AutoGeneratedSetterFuncs.cpp

rm -f src/apache2_module/ServerConfig/AutoGeneratedStruct.h
rm -f src/apache2_module/DirConfig/AutoGeneratedStruct.h
rm -f src/nginx_module/MainConfig/AutoGeneratedStruct.h
rm -f src/nginx_module/LocationConfig/AutoGeneratedStruct.h

rake src/apache2_module/ConfigGeneral/AutoGeneratedDefinitions.cpp
rake src/apache2_module/ConfigGeneral/AutoGeneratedSetterFuncs.cpp
rake src/apache2_module/ServerConfig/AutoGeneratedStruct.h
rake src/apache2_module/DirConfig/AutoGeneratedStruct.h
rake src/nginx_module/MainConfig/AutoGeneratedStruct.h
rake src/nginx_module/LocationConfig/AutoGeneratedStruct.h

echo "SPECIALVARS"

echo _httpd_mmn           %{_httpd_mmn}
echo _httpd_confdir       %{_httpd_confdir}
echo _httpd_modconfdir    %{_httpd_modconfdir}
echo _httpd_moddir        %{_httpd_moddir}
echo SOURCE1             %{SOURCE1}
echo SOURCE2             %{SOURCE2}
echo _bindir              %{_bindir}
echo _localstatedir       %{_localstatedir}
echo passenger_libdir     %{passenger_libdir}
echo passenger_archdir    %{passenger_archdir}
echo passenger_agentsdir  %{passenger_agentsdir}

echo _sbindir             %{_sbindir}
echo _mandir              %{_mandir}
echo _datadir             %{_datadir}
echo _docdir              %{_docdir}
echo _libdir              %{_libdir}
echo _libexecdir          %{_libexecdir}
echo _prefix              %{_prefix}
echo _sysconfdir          %{_sysconfdir}

mkdir -p build/support/vendor/cxx_hinted_parser

%if 0%{?rhel} < 8
export LD_LIBRARY_PATH=%{_libdir}:$LD_LIBRARY_PATH
export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=true
export GEM_PATH=%{gem_dir}:${GEM_PATH:+${GEM_PATH}}${GEM_PATH:-`ruby -e "print Gem.path.join(':')"`}
CFLAGS="${CFLAGS:-%optflags} -I/opt/cpanel/ea-brotli/include -I/opt/cpanel/ea-openssl11/include -I/opt/cpanel/libcurl/include -I/usr/include" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;
RPATH=""
RPATH="$RPATH -Wl,-rpath=/opt/cpanel/ea-brotli/lib"
RPATH="$RPATH -Wl,-rpath=/opt/cpanel/ea-openssl11/lib"
RPATH="$RPATH -Wl,-rpath=/opt/cpanel/libcurl/lib64"
RPATH="$RPATH -Wl,-rpath=/opt/cpanel/ea-apr16/lib64"
RPATH="$RPATH -Wl,-rpath=%{_libdir},--enable-new-dtags"

EXTRA_CXX_LDFLAGS="-L/usr/lib64 -L/opt/cpanel/ea-brotli/lib -L/opt/cpanel/ea-openssl11/lib -L/opt/cpanel/libcurl/lib64 -L/usr/lib64 $RPATH -lcurl -lssl -lcrypto -lgssapi_krb5 -lkrb5 -lk5crypto -lkrb5support -lssl -lcrypto -lssl -lcrypto -lbrotlidec -lbrotlienc -lbrotlicommon -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto "; export EXTRA_CXX_LDFLAGS;

FFLAGS="${FFLAGS:-%optflags}" ; export FFLAGS;

export EXTRA_CXXFLAGS="-I/opt/cpanel/ea-brotli/include -I/opt/cpanel/ea-openssl11/include -I/opt/cpanel/libcurl/include -I/usr/include $EXTRA_CXX_LDFLAGS"
%else
# this side is untested

export LD_LIBRARY_PATH=%{_libdir}:$LD_LIBRARY_PATH
export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=true
export GEM_PATH=%{gem_dir}:${GEM_PATH:+${GEM_PATH}}${GEM_PATH:-`ruby -e "print Gem.path.join(':')"`}
CFLAGS="${CFLAGS:-%optflags} -I/usr/include" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;

EXTRA_CXX_LDFLAGS="-L/usr/lib64 -lcurl -lssl -lcrypto -lgssapi_krb5 -lkrb5 -lk5crypto -lkrb5support -lssl -lcrypto -lssl -lcrypto -lbrotlidec -lbrotlienc -lbrotlicommon -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto "; export EXTRA_CXX_LDFLAGS;

FFLAGS="${FFLAGS:-%optflags}" ; export FFLAGS;
%endif

export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

rake fakeroot \
    NATIVE_PACKAGING_METHOD=rpm \
    FS_PREFIX=%{_prefix} \
    FS_BINDIR=%{_bindir} \
    FS_SBINDIR=%{_sbindir} \
    FS_DATADIR=%{_datadir} \
    FS_LIBDIR=%{_libdir} \
    FS_DOCDIR=%{_docdir} \
    RUBYLIBDIR=%{passenger_libdir} \
    RUBYARCHDIR=%{passenger_archdir} \
    APACHE2_MODULE_PATH=%{_httpd_moddir}/mod_passenger.so

# find python and ruby scripts to change their shebang

find . -name "*.py" -print | xargs sed -i '1s:^#!.*python.*$:#!/usr/bin/python2:'

cd $MYPWD

%install
set -x

echo "INSTALL BEGINS" `pwd`

cd passenger-release-%{version}

export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=true

export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

cp -a pkg/fakeroot/* %{buildroot}/

echo "PASSENGER_LIBDIR :%{passenger_libdir}:"
echo "BINDIR :%{_bindir}:"
echo "HTTPD_MODDIR :%{_httpd_moddir}:"

# Install bootstrapping code into the executables and the Nginx config script.
./dev/install_scripts_bootstrap_code.rb --ruby %{passenger_libdir} %{buildroot}%{_bindir}/* %{buildroot}%{_sbindir}/*

# Install Apache module.
mkdir -p %{buildroot}/%{_httpd_moddir}
install -pm 0755 buildout/apache2/mod_passenger.so %{buildroot}/%{_httpd_moddir}

# Install Apache config.
mkdir -p %{buildroot}%{_httpd_confdir} %{buildroot}%{_httpd_modconfdir}
sed -e 's|@PASSENGERROOT@|%{passenger_libdir}/phusion_passenger/locations.ini|g' %{SOURCE1} > passenger.conf
sed -i 's|@PASSENGERDEFAULTRUBY@|/usr/bin/ruby|g' passenger.conf
sed -i 's|@PASSENGERSO@|%{_httpd_moddir}/mod_passenger.so|g' passenger.conf
sed -i 's|@PASSENGERINSTANCEDIR@|%{_localstatedir}/run/passenger-instreg|g' passenger.conf

mkdir -p %{buildroot}/var/cpanel/templates/apache2_4
# keep version agnostic name for old ULCs :(
install -m 0640 %{SOURCE2} %{buildroot}/var/cpanel/templates/apache2_4/passenger_apps.default
# have version/package specific name for new ULCs :)
install -m 0640 %{SOURCE2} %{buildroot}/var/cpanel/templates/apache2_4/ruby-system-mod_passenger.appconf.default
# support < 100 that did not do `-system` for non-versioned rubies
install -m 0640 %{SOURCE2} %{buildroot}/var/cpanel/templates/apache2_4/rubyby-mod_passenger.appconf.default

echo %{buildroot}/var/cpanel/templates/apache2_4/mod_passenger.appconf.default
echo /var/cpanel/templates/apache2_4/passenger_apps.default
#/var/cpanel/templates/apache2_4/mod_passenger.appconf.default

%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
    sed -n /^LoadModule/p passenger.conf > 10-passenger.conf
    sed -i /^LoadModule/d passenger.conf
    touch -r %{SOURCE1} 10-passenger.conf
    install -pm 0644 10-passenger.conf %{buildroot}%{_httpd_modconfdir}/passenger.conf
%endif
touch -r %{SOURCE1} passenger.conf
install -pm 0644 passenger.conf %{buildroot}%{_httpd_confdir}/passenger.conf

# Move agents to libexec
mkdir -p %{buildroot}/%{passenger_agentsdir}
mv %{buildroot}/%{passenger_archdir}/support-binaries/* %{buildroot}/%{passenger_agentsdir}
rmdir %{buildroot}/%{passenger_archdir}/support-binaries/
sed -i 's|%{passenger_archdir}/support-binaries|%{passenger_agentsdir}|g' \
    %{buildroot}%{passenger_libdir}/phusion_passenger/locations.ini

# Instance registry to track apps
mkdir -p %{buildroot}%{_localstatedir}/run/passenger-instreg

# Install man pages into the proper location.
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_mandir}/man8
cp man/*.1 %{buildroot}%{_mandir}/man1
cp man/*.8 %{buildroot}%{_mandir}/man8

# Fix Python scripts with shebang which are not executable
chmod +x %{buildroot}%{_datadir}/passenger/helper-scripts/wsgi-loader.py

# Remove empty release.txt file
rm -f %{buildroot}%{_datadir}/passenger/release.txt

# Remove object files and source files. They are needed to compile nginx
# using "passenger-install-nginx-module", but it's not according to
# guidelines. Debian does not provide these files too, so we stay consistent.
# In the long term, it would be better to allow Fedora nginx to support
# Passenger.
rm -rf %{buildroot}%{passenger_libdir}/ngx_http_passenger_module
rm -rf %{buildroot}%{passenger_libdir}/ruby_extension_source
rm -rf %{buildroot}%{passenger_libdir}/include
rm -rf %{buildroot}%{passenger_archdir}/nginx_dynamic
rm -rf %{buildroot}%{_libdir}/passenger/common
rm -rf %{buildroot}%{_bindir}/passenger-install-*-module

cd -

BUILD=/home/abuild/rpmbuild/BUILD/passenger-release-%{version}

echo  %{buildroot}/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}
mkdir -p  %{buildroot}/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}
cp $BUILD/LICENSE %{buildroot}/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}
cp $BUILD/CONTRIBUTORS %{buildroot}/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}
cp $BUILD/CHANGELOG %{buildroot}/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}

cp $BUILD/LICENSE .
cp $BUILD/CONTRIBUTORS .
cp $BUILD/CHANGELOG .

rm -rf /usr/src/debug/build-id/*
rm -rf /usr/src/debug/passenger-release-%{version}

%clean
rm -rf %{buildroot}

%files
%config(noreplace) %{_httpd_modconfdir}/*.conf
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_confdir}/*.conf
%endif
/var/cpanel/templates/apache2_4/passenger_apps.default
/var/cpanel/templates/apache2_4/ruby-system-mod_passenger.appconf.default
/var/cpanel/templates/apache2_4/rubyby-mod_passenger.appconf.default
%{_httpd_moddir}/mod_passenger.so
%{_bindir}/passenger*
%dir %attr(755, root, root) %{_localstatedir}/run/passenger-instreg
%{passenger_libdir}
%{passenger_agentsdir}
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*
%{passenger_archdir}/passenger_native_support.so

%files doc
%doc %{_docdir}/passenger
%doc LICENSE CONTRIBUTORS CHANGELOG
%doc /opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}/LICENSE
%doc /opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}/CONTRIBUTORS
%doc /opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-%{version}/CHANGELOG

%changelog
* Tue Dec 28 2021 Dan Muey <dan@cpanel.net> - 6.0.10-2
- ZC-9589: Update DISABLE_BUILD to match OBS

* Fri Aug 13 2021 Julian Brown <julian.brown@webpros.com> - 6.0.10-1
- ZC-9201 - Initial Release

