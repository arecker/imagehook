import contextlib
import importlib.util
import importlib.machinery
import os
import pathlib
import subprocess
import tempfile
import unittest

# Import script as a library
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

spec = spec_from_loader('imagehook', SourceFileLoader(
    'imagehook', str(pathlib.Path(__file__).parent / 'imagehook')))
imagehook = module_from_spec(spec)
spec.loader.exec_module(imagehook)


@contextlib.contextmanager
def temp_repo():
    # capture current dir
    curdir = os.curdir
    # create temp dir
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)

        # change current directory
        os.chdir(d)

        # create git repo
        subprocess.run('git init'.split(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # create some new files
        (d / 'test-1.jpg').touch()
        (d / 'subdir').mkdir()
        (d / 'subdir/test-2.jpg').touch()

        # stage everything
        subprocess.run('git add -A'.split(), check=True)

        try:
            # yield directory
            yield pathlib.Path(d)
        finally:
            # restore original current directory
            os.chdir(curdir)


class TestImageHook(unittest.TestCase):
    def test_fetch_new_staged_files(self):
        with temp_repo() as p:
            actual = imagehook.fetch_new_staged_files()

        self.assertEqual(actual, [
            'subdir/test-2.jpg',
            'test-1.jpg',
        ])


if __name__ == '__main__':
    unittest.main()
