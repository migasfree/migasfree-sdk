# -*- coding: utf-8 -*-

import os

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    try:
        import pkg_resources

        def version(package):
            return pkg_resources.get_distribution(package).version

        PackageNotFoundError = Exception
    except ImportError:
        # No pkg_resources
        def version(package):
            raise Exception()

        PackageNotFoundError = Exception

try:
    __version__ = version("migasfree-sdk")
except (PackageNotFoundError, Exception):
    # Fallback for when the package is not installed (e.g. direct execution or dev mode)
    try:
        # VERSION is in the root directory (one level up from this file)
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION"
        )
        with open(path, "r") as f:
            __version__ = f.read().strip()
    except (IOError, OSError):
        __version__ = "unknown"
