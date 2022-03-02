#! /usr/bin/env python3
import sys
import io
import os
import fcntl
import signal
import threading
import AIS
import zmq
import subprocess
from PyQt5 import Qt

run_reader = threading.Event()

def read_data(ais):
    # connect internal data socket
    ctx = zmq.Context()
    skt = ctx.socket(zmq.PULL)
    skt.connect(ais.get_zmq_address())
    # start gnuais subprocess
    with subprocess.Popen(
        ['/usr/bin/stdbuf','-oL','/usr/bin/gnuais','-l','/dev/stdin','-o','stderr'],
        bufsize=0,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        close_fds=True) as gnuais:
        # set stdout of gnuais to non-blocking
        fd = gnuais.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        text = []
        while not run_reader.is_set():
            if skt.poll(timeout=100)!=0:
                buf = skt.recv()
                gnuais.stdin.write(buf)
            # try a read.. expect BlockingIOError when empty..
            try:
                buf = gnuais.stdout.read(1)
                if buf:
                    c = chr(buf[0])
                    if '\n'==c:
                        line = ''.join(text)
                        text = []
                        print('AIS:'+line)
                        if ais.doGUI:
                            ais.set_ais_string(line)
                    else:
                        text.append(c)
            except BlockingIOError:
                pass

def main():
    # process cmdline - currently enable/disable GUI
    doGUI = False
    for arg in sys.argv[1:]:
        if '-qt' == arg:
            doGUI = True
        else:
            print(f'usage: {sys.argv[0]} [-qt]')
            sys.exit(0)

    # duplicated from AIS.main - but with our threading bits included
    if doGUI:
        qapp = Qt.QApplication(sys.argv)
    tb = AIS.AIS(doGUI)
    tb.start()
    if doGUI:
        tb.show()

    def quitting():
        tb.stop()
        if doGUI:
            tb.wait()
        run_reader.set()
        thr.join()

    def sig_handler(sig=None, frame=None):
        if doGUI:
            Qt.QApplication.quit()
        else:
            quitting()
            sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    if doGUI:
        timer = Qt.QTimer()
        timer.start(500)
        timer.timeout.connect(lambda: None)
        qapp.aboutToQuit.connect(quitting)

    # wait 2 seconds before starting reader to allow zmq socket to be created
    thr = threading.Timer(2, read_data, args=[tb])
    thr.start()
    if doGUI:
        qapp.exec_()
    else:
        print('Press <Return> to terminate')
        sys.stdin.readline()
        quitting()

if __name__ == '__main__':
    main()
