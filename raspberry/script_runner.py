# Run scripts found in a specific folder. This allows a single raspberry pi
# to be shared between many students - they simply scp their code onto the box
import os
import shutil
import signal
import subprocess
import sys
import time

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

SCRIPT_DIR = "/home/pi/userscripts"
FINISHED_SCRIPTS_DIR = '/home/pi/userscripts/finished'
ERROR_SCRIPTS_DIR = '/home/pi/userscripts/error'
DEFAULT_TIMEOUT = 20


def print_python_script(filename):
    code = open(filename, "rb").read()
    highlight(code, PythonLexer(), TerminalFormatter(), sys.stdout)


def get_user_permission(filename):
    timeout = None
    opt = raw_input("Are you happy to run {0}? [y/n/print]: ".format(filename))
    if opt == 'print':
        print_python_script("{0}/{1}".format(SCRIPT_DIR, filename))
        return get_user_permission(filename)
    elif opt == 'y':
        timeout = raw_input("How long should the script be allowed to run for?"
                        " [default: {0} seconds]: ".format(DEFAULT_TIMEOUT))

    if not timeout:
        timeout = DEFAULT_TIMEOUT

    return opt == 'y', int(timeout)


def wait_with_feedback(timeout):
    start = time.time()
    while time.time() - start < timeout:
        print "{0} of {1} secs...".format(int(time.time() - start), timeout)
        time.sleep(1)


def attempt_run(filename):
    do_run, timeout = get_user_permission(filename)
    if do_run:
        process = subprocess.Popen([
            sys.executable,
            '{0}/{1}'.format(SCRIPT_DIR, filename),
            ])
        time.sleep(2)
        process.poll()
        if process.returncode == 1:
            error(filename, "Error running the file. Return code 1")
            return
        print "{0} running on pid {1}".format(filename, process.pid)
        wait_with_feedback(timeout - 2)
        try:
            print "Killing {0}".format(process.pid)
            os.kill(process.pid, signal.SIGKILL)
        except OSError as e:
            print "OSError while killing:\n{0}".format(dir(e))
        finished(filename)
    else:
        opt = raw_input("Quit? or move this file to the error folder?: [q,m]")
        if opt == 'q':
            sys.exit()
        elif opt == 'm':
            error(filename, "Moved away.")


def get_unique_filename(filepath):
    "Add an integer to the end of the filename until it's unique"
    new_file_name = filepath
    index = 0
    while os.path.exists(new_file_name):
        new_file_name = "{0}.{1}".format(filepath, index)
        index += 1
    return new_file_name


def finished(filename):
    "Move the file into the finished scripts dir."
    print "FINISHED: {0}".format(filename)
    new_file_name = get_unique_filename(
                        "{0}/{1}".format(FINISHED_SCRIPTS_DIR, filename))
    shutil.move("{0}/{1}".format(SCRIPT_DIR, filename), new_file_name)


def error(filename, errorstring):
    "Print an error and move the file into an error directory"
    print "ERROR: {0} - {1}".format(filename, errorstring)
    new_error_file_name = get_unique_filename(
                "{0}/{1}".format(ERROR_SCRIPTS_DIR, filename))
    shutil.move("{0}/{1}".format(SCRIPT_DIR, filename), new_error_file_name)


def main():
    while 1:
        for filename in os.listdir(SCRIPT_DIR):
            print "Looking at {0}".format(filename)
            if not os.path.isdir("{0}/{1}".format(SCRIPT_DIR, filename)):
                if filename.endswith(".py"):
                    attempt_run(filename)
                else:
                    error(filename, "Not a recognized file")
        time.sleep(3)


if __name__ == '__main__':
    main()
