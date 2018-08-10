#!venv/bin/python3
# Note: The shebang will be added with the correct absolute installation path by 'install' script.

from webmsg import wsgi

from django.core.management import call_command

if __name__ == '__main__':
    import sys
    addr = '127.0.0.1:8000'
    if len(sys.argv) >= 2:
        addr = sys.argv[1]  # 0 will always be the file name
    call_command('runserver', addr)
