import subprocess
import os
from .exceptions import CommandNotFound, CommandCalledError, CopyFileError, ValueMandatoryError
import logging
from .utils import read_toml_file, config_path, input_confirm, all_project_files, all_project_path


class Management:

    def __init__(self, *args, **kwargs):
        self.base_dir = config_path()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def install_setup(self):
        self._create_directories()
        self._move_files()
        self._backup_old_rules()
        self._set_systemctl()
        logging.info('Installation completed successfully.')
    
    def start_setup(self):
        self._delete_rules()
        self._add_rules()
        self._replace_file_config_enable()
        logging.info('Started successfully.')
    
    def stop_setup(self):
        self._delete_rules()
        logging.info('Stopped successfully.')

    def restart_setup(self):
        self._delete_rules()
        self._add_rules()
        self._replace_file_config_enable()
        logging.info('Successfully restarted.')

    def _set_systemctl(self):
        """
        Reload the systemd manager configuration
        """
        self.run_command('systemctl-reload')
        self.run_command('systemctl-enable')

    def _create_directories(self):
        """
        create all the directories necessary to run the project
        """
        [
            os.makedirs(path, exist_ok=True)
            for path in all_project_path().values()
            if not os.path.exists(path)
        ]

        logging.info('Directories created successfully.')

    def _replace_file_config_enable(self):

        available_path = all_project_path('config-available')
        active_path = all_project_path('config-active')

        files = os.listdir(available_path)

        for file in files:
            specific = [
                {
                    'src': f'{available_path}/{file}',
                    'dst': f'{active_path}/{file}',
                    'success_message': f'File {file} update successfully.'
                }
            ]
            self._move_files(specific_file=specific)

    def _move_files(self, specific_file=None):
        """
        Moves all files necessary to run the project
        """
        if specific_file:
            files = specific_file
        else:
            files = [
                {
                    'src': all_project_files('src_service'),
                    'dst': all_project_files('dst_service'),
                    'success_message': 'File iptables-tools.service copy successfully.'
                },
                {
                    'src': all_project_files('src_default'),
                    'dst': all_project_files('dst_default'),
                    'success_message': 'File available default.toml copy successfully.'
                },
                {
                    'src': all_project_files('src_default'),
                    'dst': all_project_files('active_default'),
                    'success_message': 'File enabled default.toml update successfully.'
                }
            ]

            if all([
                os.path.exists(file.get("dst"))
                for file in files
            ]):
                if not input_confirm(
                    "Configuration files already exist. Do you want to replace them?"
                ):
                    logging.info('Skipping file copy')
                    return

        for file in files:
            input = f'cp -f {file.get("src")} {file.get("dst")}'
            result = self._run_subprocess(input)

            if result.returncode == 0:
                logging.info(file.get('success_message'))
            else:
                raise CopyFileError(str(result.stderr))

    def _backup_old_rules(self):
        """
        Create a backup of the old rules
        """
        files = [
            all_project_files('bkp_rules_v4'),
            all_project_files('bkp_rules_v6')
        ]
        
        if all([os.path.exists(file) for file in files]):
            if not input_confirm(
                "Backup files already exist. Do you want to replace them?"
            ):
                return

        self.run_command('export-backup-rules')

    def _add_rules(self):
        available_path = all_project_path('config-available')
        files = os.listdir(available_path)

        for file in files:
            self._set_rules(
                type_run='insert',
                file_toml=f'{available_path}/{file}'
            )

        logging.info('Rules added successfully.')

    def _delete_rules(self):
        active_path = all_project_path('config-active')
        files = os.listdir(active_path)

        if not files:
            logging.info('No rules to delete.')
            return

        for file in files:
            self._set_rules(
                type_run='delete',
                file_toml=f'{active_path}/{file}'
            )
        logging.info('Rules deleted successfully.')

    def run_command(self, command):
        if cmd := self._get_alias_command_list(command):

            result = self._run_subprocess(cmd.get('cmd'))
            if result.returncode == 0:
                logging.info(cmd.get('success_message'))
                return
            else:
                raise CommandCalledError('run', command, result.stderr)

        raise CommandNotFound
    
    def _run_subprocess(self, command):
        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

    def _get_alias_command_list(self, command):
        return self.alias_command_list().get(command)
    
    def alias_command_list(self):
        
        return {
            'export-backup-rules': {
                'cmd': f"iptables-save > {all_project_files('bkp_rules_v4')} && ip6tables-save > {all_project_files('bkp_rules_v6')}",
                'description': 'Export backup IPv4 and IPv6 rules in iptables format.',
                'success_message': f"Successful IPv4 and IPv6 backup rules in {all_project_files('bkp_rules_v4')} and {all_project_files('bkp_rules_v6')}."
            },
            'import-backup-rules': {
                'cmd': f"iptables-restore < {all_project_files('bkp_rules_v4')} && ip6tables-restore < {all_project_files('bkp_rules_v6')}",
                'description': 'Import backup IPv4 and IPv6 rules in iptables format.',
                'success_message': f"Restored successful IPv4 and IPv6 backup rules in {all_project_files('bkp_rules_v4')} and {all_project_files('bkp_rules_v6')}."
            },
            'export-rules': {
                'cmd': f"iptables-save > {all_project_files('exp_rules_v4')} && ip6tables-save > {all_project_files('exp_rules_v6')}",
                'description': 'Export IPv4 and IPv6 rules in iptables format.',
                'success_message': f"Rules IPv4 and IPv6 exported successfully in {all_project_files('exp_rules_v4')} and {all_project_files('exp_rules_v6')}."
            },
            'import-rules': {
                'cmd': f"iptables-restore < {all_project_files('exp_rules_v4')} && ip6tables-restore < {all_project_files('exp_rules_v6')}",
                'description': 'Import IPv4 and IPv6 rules in iptables format.',
                'success_message': 'Rules IPv4 and IPv6 imported successfully.'
            },
            'export-rules-v4': {
                'cmd': f"iptables-save > {all_project_files('exp_rules_v4')}",
                'description': 'Export IPv4 rules in iptables format.',
                'success_message': f"Rules IPv4 exported successfully in {all_project_files('exp_rules_v4')}."
            },
            'import-rules-v4': {
                'cmd': f"iptables-restore < {all_project_files('exp_rules_v4')}",
                'description': 'Import IPv4 rules in iptables format.',
                'success_message': 'Rules IPv4 imported successfully.'
            },
            'export-rules-v6': {
                'cmd': f"ip6tables-save > {all_project_files('exp_rules_v6')}",
                'description': 'Export IPv6 rules in iptables format.',
                'success_message': f"Rules v6 exported successfully in {all_project_files('exp_rules_v6')}."
            },
            'import-rules-v6': {
                'cmd': f"ip6tables-restore < {all_project_files('exp_rules_v6')}",
                'description': 'Import IPv6 rules in iptables format.',
                'success_message': 'Rules IPv6 imported successfully.'
            },
            'systemctl-reload': {
                'cmd': 'systemctl daemon-reload',
                'description': 'Reload the systemd manager configuration.',
                'success_message': 'Systemd manager configuration reloaded successfully.'
            },
            'systemctl-enable': {
                'cmd': 'systemctl enable iptables-tools',
                'description': 'Enabled the iptables-tools service.',
                'success_message': 'Service iptables-tools enabled successfully.'
            },
        }

    def _set_rules(self, type_run, file_toml):

        config = read_toml_file(file_toml)

        if list_rules := self._format_toml(
            data=config,
            type_run=type_run
        ):
            self._run_rules(list_rules, type_run)

    def _format_toml(self, data, type_run):
        """
        format configuration file
        """
        list_rules = []
        
        for config in data.values():
            for _, values in config.items():
                self._validate_mandatory_parameters(values)
                protocol = values.get('protocol')
                chain = values.get('chain')
                port = values.get('port')                               

                if rules := self._check_rules(
                    type_run = type_run,
                    chain = chain,
                    protocol = protocol,
                    port = port,
                    info = values
                ):
                    list_rules.extend(rules)                    

        return list_rules        

    def _run_rules(self, list_commands, type_run):
        """
        set rules in iptables
        """
        for command in list_commands:
            input = ' '.join(command)
            result = self._run_subprocess(input)

            if result.returncode != 0 and type_run == 'insert':
                raise CommandCalledError('run', input, result.stderr)      

    def _check_rules(self, type_run, chain, protocol, port, info):
        """
        Checks if the accept and drop rules exist in the configuration
        file default.toml
        """
        list_rules = []
        targets = ['drop', 'accept']
        versions = ['ipv4', 'ipv6']

        for target in targets:
            for version in versions:
                if rules := self._validate_optional_parameters(
                    version=version,
                    data=info,
                    key=target,
                    chain=chain
                ):
                    for rule in rules:
                        list_rules.append(
                            self._format_rules(
                                version = version,
                                type_run = type_run,
                                chain = chain,
                                protocol = protocol,
                                port = port,
                                info = rule,
                                target = target
                            )
                        )

        return list_rules

    def _format_rules(self, version, type_run, chain, protocol, port, info, target):
        input = [
            self._generate_rule_case(
                version,
                1
            ),
            self._generate_rule_case(type_run, 1),
            chain,
            self._generate_rule_case('src', info.get('src')),
            self._generate_rule_case('dst', info.get('dst')),
            self._generate_rule_case('protocol', protocol),
            self._generate_rule_case('port', port),
            self._generate_rule_case(
                'comment',
                info.get('comment')
            ),
            self._generate_rule_case('target', target)
        ]
        [input.remove(None) for _ in range(input.count(None))]

        return input

    def _validate_mandatory_parameters(self, data):
        """
        Validate mandatory parameters in configuration file default.toml
        """
        mandatory = ['protocol', 'chain', 'port']

        for key in mandatory:
            if not data.get(key):
                raise ValueMandatoryError(
                    return_message=key,
                    banner_message_plus=data
                )

    def _validate_optional_parameters(self, version, data, key, chain):
        """
        Validate optional parameters in configuration file default.toml
        """
        if not data.get(version):
            logging.warning(f"Key {version} not found in chain {chain}")
            return

        if not data.get(version).get(key):
            logging.warning(f"Key {version}.{key} not found in chain {chain}")
            return

        if not data.get(version).get(key).get('mapping'):
            logging.warning(f"Key {version}.{key}.mapping not found in chain {chain}")
            return
        
        return data.get(version).get(key).get('mapping')

    def _generate_rule_case(self, key, value):
        if not value:
            return
        
        options = {
            'ipv4': 'iptables',
            'ipv6': 'ip6tables',
            'src': f'-s {value}',
            'dst': f'-d {value}',
            'port': f'--dport {value}',
            'protocol': f'-p {value} -m {value}',
            'comment': f'-m comment --comment "{value}"',
            'insert': '-I',
            'delete': '-D',
            'target': '-j ACCEPT' if value == 'accept' else '-j DROP'
        }

        return options.get(key)
