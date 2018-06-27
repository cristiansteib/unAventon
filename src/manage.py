#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unAventon.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    is_testing = 'test' in sys.argv
    is_coverage_running = False

    try:
        if is_testing:
            import coverage
            is_coverage_running = True

            cov = coverage.coverage(
                source=['unAventonApp'],
                omit=[
                    '*/tests/*',
                    '*/migrations/*',
                    '*/__init__.py',
                    '*/apps.py',
                    '*/urls.py',
                    '*/admin.py',
                    '*/tests.py'],
            )
            cov.exclude('  pragma: no cover')
            cov.exclude('raise AssertionError')
            cov.exclude('raise NotImplementedError')
            cov.exclude('if __name__ == .__main__.:')
            cov.exclude('from')
            cov.exclude('import')
            cov.erase()
            cov.start()

    except ImportError:
        print("Deberias instalar los requirements.txt")


    execute_from_command_line(sys.argv)


    if is_testing and is_coverage_running:
        cov.stop()
        cov.save()
        cov.html_report(directory='coverageTestHTML')
