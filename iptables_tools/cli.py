import argparse
from iptables_tools.controls.exceptions import CommandNotFound, CommandPermissionError, RunCommandError
from iptables_tools.controls.iptables import Management 


class Main(Management):

    def __call__(self, method_name, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            method = getattr(self, method_name)
            return method(command)
        except PermissionError as err:
            self.roolback()
            raise CommandPermissionError(method_name, command, err) from None
        except RunCommandError:
            self.roolback()
            raise RunCommandError(method_name, command) from None
        except CommandNotFound:
            self.roolback()
            raise CommandNotFound(method_name, command) from None
        except Exception:
            self.roolback()
            raise
    
    def install(self, command):
        self.install_setup()

    def start(self, command):
        self.start_setup()
    
    def stop(self, command):
        self.stop_setup()

    def restart(self):
        self.restart_setup()

    def run(self, command):
        if not command:
            raise RunCommandError

        self.run_command(command) 

    def roolback(self, command=None):
        self.run_command('import-backup-rules')

def cli():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="method")

    # Subparser para o método 'install'
    subparsers.add_parser('install', help="Instala o projeto")
    subparsers.add_parser('roolback', help="Restaura as regras de firewall para o estado anterior a instalação")    
    subparsers.add_parser('start', help="Utilize o systemd para iniciar o serviço.")
    subparsers.add_parser('stop', help="Utilize o systemd para iniciar o serviço.")
    subparsers.add_parser('restart', help="Utilize o systemd para iniciar o serviço.")

    # Subparser para o método 'run'
    execute_parser = subparsers.add_parser('run', help="Executa um comando específico")
    # Adiciona as opções para o subparser 'run'
    for option, value in Management().alias_command_list().items():
        execute_parser.add_argument(
            f"--{option}",
            dest="command",
            action='store_const',
            const=option,
            help=value.get('description')
        )

    args = parser.parse_args()

    method = args.method
    command = args.command if hasattr(args, 'command') else None

    Main(args)(method, command)

if __name__ == "__main__":
    cli()