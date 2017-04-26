#!/bin/bash
wget "http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz"
tar xzf PyQt4_gpl_x11-4.12.tar.gz
cd PyQt4_gpl_x11-4.12
python configure.py --verbose --confirm-license --no-designer-plugin --no-qsci-api --no-timestamp
make -j2
make install
