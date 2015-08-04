#!/bin/bash

BUILD_DIR=build
INSTALL_DIR=usr/local/share/kodi/addons/plugin.xbianconfig
ADDON_DIR=xbianconfig
LOCALE_DIR=usr/share/locale

str='strip'
strargs='--strip-unneeded'
tot=0

if ! dpkg-architecture -iarmhf; then
    arm-linux-gnueabihf-strip > /dev/null 2>&1
    [ $? -eq '127' ] && { str=''; true; } || str='arm-linux-gnueabihf-strip'
    arm-linux-gnu-strip > /dev/null 2>&1
    [ $? -eq '127' ] && { str=''; true; }|| str='arm-linux-gnu-strip'
    [ -z "$str" ] && { echo "please install binutils-arm-linux-gnueabihf on Debian or arm-linux-gnu-strip on CentOS"; str=''; true; }
fi

# Make sure to remove build dir after building the package
trap "rm -rf $BUILD_DIR" EXIT SIGINT SIGTERM

mkdir -p $BUILD_DIR/$INSTALL_DIR
mkdir -p $BUILD_DIR/DEBIAN
cp -r $ADDON_DIR/* $BUILD_DIR/$INSTALL_DIR
cp -r debian/* $BUILD_DIR/DEBIAN

# Compile translations
for f in $(find po -type f -name "*.po"); do
    base=$(basename $f)
    language=${base%.*}
    dir=$BUILD_DIR/$LOCALE_DIR/$language/LC_MESSAGES/
    mkdir -p $dir
    msgfmt -o $dir/xbian-config.mo -v $f
done

find $BUILD_DIR/$INSTALL_DIR -name "*.pyc" -delete

package=$(cat debian/control | grep Package | awk '{print $2}')
version1=$(date +%Y%m%d)
version2=0
while [ -f "$package-$version1-$version2.deb" ]; do
    version2=$(($version2 + 1))
done
version=$version1-$version2
sed -i "s%__DATE__%$version%g" $BUILD_DIR/DEBIAN/control

cd $BUILD_DIR
find ./ -type f -print0 | xargs -0 -L1 printf "%s\n" | while read f; do [ -z "$str" ] || $str $strargs "$f" 2>/dev/null; s=$(stat -c %s "$f"); tot=$((tot + (s/1024)+1)); echo $tot > ../size.txt; done
printf "Installed-Size: %u\n" $(cat ../size.txt) >> ./DEBIAN/control
rm ../size.txt
find ./ -type f ! -regex '.*.hg.*' ! -regex '.*?debian-binary.*' ! -regex '.*?DEBIAN.*' -printf '%P\0' | sort -z| xargs --null md5sum > DEBIAN/md5sums
cd ..

# FIXME: We should really build the package instead of dpkg-deb here
fakeroot dpkg-deb -b $BUILD_DIR "$package-$version.deb"
