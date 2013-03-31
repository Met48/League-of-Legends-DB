from collections import namedtuple
import difflib
import os.path
from StringIO import StringIO
import time


class FileTransaction(object):
    """
    Safely write to multiple files.

    While this is not an atomic operation,
    the following safeguards are in place:
        Files are opened in append mode to start.
        New contents are not written to the original file.
        Diffs can be generated to review all the changes.
    """

    files = []
    ROW = namedtuple('TransactionRow', ['handle_original', 'handle_archive',
                     'handle_diff', 'contents', 'buf', 'filename'])

    def __init__(self, archives_path):
        self.archives_path = archives_path
        self.timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    def open(self, filename, diff=True, binary=False):
        """Start managing a file."""

        if binary:
            mode = 'ab+'
        else:
            mode = 'a+'

        # Open all handles
        handle_original = open(filename, mode)
        dir, name = os.path.split(filename)
        handle_archive = open(
            os.path.join(
                dir,
                self.archives_path,
                '%s_%s' % (self.timestamp, name),
            ),
            mode
        )
        if diff:
            handle_diff = open(filename + '.diff', 'a+')
        else:
            handle_diff = None

        # Read original file contents
        handle_original.seek(0)
        contents = handle_original.read()

        buf = StringIO()

        row = self.ROW(handle_original, handle_archive, handle_diff,
                       contents, buf, filename)
        self.files.append(row)

        return buf

    def read(self, filename):
        """Get the original contents of a managed file."""

        for row in self.files:
            if row.filename == filename:
                return row.contents
        raise ValueError("No such file is opened.")

    def buffer(self, filename):
        """Get the write buffer for a managed file."""

        for row in self.files:
            if row.filename == filename:
                return row.buf
        raise ValueError("No such file is opened.")

    def diff(self):
        """Generate diffs for managed files."""

        for row in self.files:
            if not row.handle_diff:
                continue

            # Create diff
            name = os.path.basename(row.filename)
            diff = difflib.unified_diff(
                row.contents.split('\n'),
                row.buf.getvalue().split('\n'),
                fromfile=name,
                tofile="new_" + name,
            )
            diff = '\n'.join(diff)

            # Output diff to file
            row.handle_diff.seek(0)
            row.handle_diff.truncate()
            row.handle_diff.seek(0)
            row.handle_diff.write(diff)
            row.handle_diff.flush()

    def complete(self):
        """Write buffered output to managed files."""

        for row in self.files:
            output = row.buf.getvalue()
            for handle in [row.handle_archive, row.handle_original]:
                handle.seek(0)
                handle.truncate()
                handle.seek(0)
                handle.write(output)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Close all open file objects
        for row in self.files:
            handles = [
                row.handle_original,
                row.handle_archive,
                row.handle_diff,
            ]
            for handle in handles:
                if not handle:
                    continue
                try:
                    handle.close()
                except IOError:
                    pass
