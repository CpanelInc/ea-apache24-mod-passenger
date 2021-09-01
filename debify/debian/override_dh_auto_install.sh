#!/bin/bash

source debian/vars.sh

set -x

echo "INSTALL BEGINS" `pwd`
cd passenger-release-$version

export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=true
export LANG=en_US.utf-8
export LANGUAGE=en_US.utf-8
export LC_ALL=en_US.utf-8

cp -R pkg/fakeroot $DEB_INSTALL_ROOT

echo "PASSENGER_LIBDIR :$passenger_libdir:"
echo "BINDIR :$_bindir:"
echo "HTTPD_MODDIR :$_httpd_moddir:"
# Install bootstrapping code into the executables and the Nginx config script.
./dev/install_scripts_bootstrap_code.rb --ruby $passenger_libdir $DEB_INSTALL_ROOT$_bindir/* $DEB_INSTALL_ROOT$_sbindir/*
# Install Apache module.
mkdir -p $DEB_INSTALL_ROOT/$_httpd_moddir
install -pm 0755 buildout/apache2/mod_passenger.so $DEB_INSTALL_ROOT/$_httpd_moddir
# Install Apache config.
mkdir -p $DEB_INSTALL_ROOT$_httpd_confdir $DEB_INSTALL_ROOT$_httpd_modconfdir
sed -e "s|@PASSENGERROOT@|$passenger_libdir/phusion_passenger/locations.ini|g" $SOURCE1 > passenger.conf
sed -i "s|@PASSENGERDEFAULTRUBY@|/usr/bin/ruby|g" passenger.conf
sed -i "s|@PASSENGERSO@|$_httpd_moddir/mod_passenger.so|g" passenger.conf
sed -i "s|@PASSENGERINSTANCEDIR@|$_localstatedir/run/passenger-instreg|g" passenger.conf

mkdir -p $DEB_INSTALL_ROOT/var/cpanel/templates/apache2_4
# keep version agnostic name for old ULCs :(
install -m 0640 $SOURCE2 $DEB_INSTALL_ROOT/var/cpanel/templates/apache2_4/passenger_apps.default
# have version/package specific name for new ULCs :)
install -m 0640 $SOURCE2 $DEB_INSTALL_ROOT/var/cpanel/templates/apache2_4/ruby-system-mod_passenger.appconf.default
# support < 100 that did not do `-system` for non-versioned rubies
install -m 0640 $SOURCE2 $DEB_INSTALL_ROOT/var/cpanel/templates/apache2_4/rubyby-mod_passenger.appconf.default
echo $DEB_INSTALL_ROOT/var/cpanel/templates/apache2_4/mod_passenger.appconf.default
echo /var/cpanel/templates/apache2_4/passenger_apps.default
#/var/cpanel/templates/apache2_4/mod_passenger.appconf.default

sed -n /^LoadModule/p passenger.conf > 10-passenger.conf
sed -i /^LoadModule/d passenger.conf
touch -r $SOURCE1 10-passenger.conf
install -pm 0644 10-passenger.conf $DEB_INSTALL_ROOT$_httpd_modconfdir/passenger.conf

touch -r $SOURCE1 passenger.conf
install -pm 0644 passenger.conf $DEB_INSTALL_ROOT$_httpd_confdir/passenger.conf
# Move agents to libexec
mkdir -p $DEB_INSTALL_ROOT/$passenger_agentsdir
mv $DEB_INSTALL_ROOT/$passenger_archdir/support-binaries/* $DEB_INSTALL_ROOT/$passenger_agentsdir
rmdir $DEB_INSTALL_ROOT/$passenger_archdir/support-binaries/
sed -i "s|$passenger_archdir/support-binaries|$passenger_agentsdir|g" \
    $DEB_INSTALL_ROOT$passenger_libdir/phusion_passenger/locations.ini
# Instance registry to track apps
mkdir -p $DEB_INSTALL_ROOT$_localstatedir/run/passenger-instreg
# Install man pages into the proper location.
mkdir -p $DEB_INSTALL_ROOT$_mandir/man1
mkdir -p $DEB_INSTALL_ROOT$_mandir/man8
cp man/*.1 $DEB_INSTALL_ROOT$_mandir/man1
cp man/*.8 $DEB_INSTALL_ROOT$_mandir/man8
# Fix Python scripts with shebang which are not executable
chmod +x $DEB_INSTALL_ROOT$_datadir/passenger/helper-scripts/wsgi-loader.py
# Remove empty release.txt file
rm -f $DEB_INSTALL_ROOT$_datadir/passenger/release.txt

# Remove object files and source files. They are needed to compile nginx
# using "passenger-install-nginx-module", but it's not according to
# guidelines. Debian does not provide these files too, so we stay consistent.
# In the long term, it would be better to allow Fedora nginx to support
# Passenger.
rm -rf $DEB_INSTALL_ROOT$passenger_libdir/ngx_http_passenger_module
rm -rf $DEB_INSTALL_ROOT$passenger_libdir/ruby_extension_source
rm -rf $DEB_INSTALL_ROOT$passenger_libdir/include
rm -rf $DEB_INSTALL_ROOT$passenger_archdir/nginx_dynamic
rm -rf $DEB_INSTALL_ROOT$_libdir/passenger/common
rm -rf $DEB_INSTALL_ROOT$_bindir/passenger-install-*-module

cd -

BUILD=/home/abuild/rpmbuild/BUILD/passenger-release-$version
echo  $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
mkdir -p  $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp $BUILD/LICENSE $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp $BUILD/CONTRIBUTORS $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp $BUILD/CHANGELOG $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp $BUILD/LICENSE .
cp $BUILD/CONTRIBUTORS .
cp $BUILD/CHANGELOG .
rm -rf /usr/src/debug/build-id/*
rm -rf /usr/src/debug/passenger-release-$version

mkdir -p $DEB_INSTALL_ROOT/etc
mkdir -p $DEB_INSTALL_ROOT/usr/bin
mkdir -p $DEB_INSTALL_ROOT/usr/lib64
mkdir -p $DEB_INSTALL_ROOT/etc/apache2/conf.d
mkdir -p $DEB_INSTALL_ROOT/usr/share/passenger/phusion_passenger/admin_tools.rb.tmpdir
mkdir -p $DEB_INSTALL_ROOT/var/run/passenger-instreg

cp -R $DEB_INSTALL_ROOT/opt/cpanel/root/etc $DEB_INSTALL_ROOT
cp -R $DEB_INSTALL_ROOT/opt/cpanel/root/usr $DEB_INSTALL_ROOT
cp -R $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc $DEB_INSTALL_ROOT/usr/share

gzip $DEB_INSTALL_ROOT/usr/share/man/man1/passenger-config.1
gzip $DEB_INSTALL_ROOT/usr/share/man/man8/passenger-memory-stats.8
gzip $DEB_INSTALL_ROOT/usr/share/man/man8/passenger-status.8

cp ./passenger-release-$version/CHANGELOG $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp ./passenger-release-$version/CONTRIBUTORS $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp ./passenger-release-$version/LICENSE $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version

mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24-mod-passenger-doc-$version
cp $DEB_INSTALL_ROOT/opt/cpanel/ea-apache24/root/usr/share/doc/ea-apache24-mod-passenger-doc-$version/* $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24-mod-passenger-doc-$version

echo "FILELIST :$DEB_INSTALL_ROOT:"
find . -type f -print | sort

