"""Run MySQL feature tests against a disposable loopback-only local instance."""
from argparse import ArgumentParser
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--server-executable', required=True, help='Path to mysqld.exe / mysqld; no existing service is used.')
    args = parser.parse_args()
    executable = Path(args.server_executable).resolve()
    if not executable.is_file():
        parser.error('MySQL server executable does not exist.')
    basedir = executable.parent.parent
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    with tempfile.TemporaryDirectory(prefix='teachtrack-mysql-', ignore_cleanup_errors=True) as tmp:
        data = Path(tmp) / 'data'
        print('Initializing disposable local MySQL data directory.', flush=True)
        result = subprocess.run([str(executable), '--no-defaults', '--initialize-insecure',
                                 f'--basedir={basedir}', f'--datadir={data}', '--console'],
                                capture_output=True, text=True, timeout=120, creationflags=flags)
        if result.returncode:
            raise SystemExit('Temporary MySQL initialization failed: ' + result.stderr[-2000:])
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        with (Path(tmp) / 'server.log').open('w') as log:
            server = subprocess.Popen([str(executable), '--no-defaults', f'--basedir={basedir}',
                                       f'--datadir={data}', '--bind-address=127.0.0.1', f'--port={port}',
                                       '--mysqlx=0', '--skip-log-bin', '--skip-ssl', '--console'],
                                      stdout=log, stderr=log, creationflags=flags)
            try:
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError('Temporary MySQL server exited before accepting connections.')
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.2):
                            break
                    except OSError:
                        time.sleep(.2)
                else:
                    raise RuntimeError('Temporary MySQL did not become ready.')
                env_file = Path(tmp) / '.env.mysql-test'
                env_file.write_text(f'DATABASE_URL=mysql://root@127.0.0.1:{port}/mysql\n'
                                    f'SECRET_KEY={secrets.token_urlsafe(64)}\n'
                                    'MYSQL_SSL_MODE=DISABLED\nMYSQL_CONNECT_TIMEOUT=10\n')
                print('Temporary MySQL is bound to loopback. Existing PC services are untouched.', flush=True)
                result = subprocess.run([sys.executable, str(ROOT / 'tools/verify_mysql.py'),
                                         '--env-file', str(env_file), '--run-tests'], cwd=ROOT)
            finally:
                try:
                    import mysql.connector
                    connection = mysql.connector.connect(user='root', host='127.0.0.1', port=port,
                                                         ssl_disabled=True, use_pure=True, connection_timeout=3)
                    try:
                        connection.cursor().execute('SHUTDOWN')
                    finally:
                        connection.close()
                    server.wait(timeout=20)
                except Exception:
                    if server.poll() is None:
                        server.terminate()
                        server.wait(timeout=20)
        print('Disposable local MySQL stopped.', flush=True)
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
