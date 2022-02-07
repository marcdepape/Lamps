update to jessie (/etc/apt/sources.list) 

# apt-get...

## remove
```
weston  # seems to conflict with gir1.2??
```

## install
```
gstreamer1.0
gstreamer1.0-plugins-*
gir1.2-gstreamer-1.0
python3-gst-1.0

# for building gst-rtsp-server
autoconf
libtool
gtk-doc-tools
libgstreamer-plugins-{base,bad}1.0
libgirepository1.0-dev
```

get and build gst-rtsp-server (1.4)
