xbian-config-python
=================

```
cd /home/xbian
rm -r xbian-config-python
git clone --depth 5 https://github.com/xbianonpi/xbian-config-python.git
rm -r /home/xbian/.xbmc/addons/plugin.xbianconfig
cd xbian-config-python
mkdir /home/xbian/.xbmc/addons/plugin.xbianconfig
cp -R * /home/xbian/.xbmc/addons/plugin.xbianconfig/
chown -R xbian:xbian /home/xbian/.xbmc/addons/plugin.xbianconfig/
```
