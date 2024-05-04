import toml
from pathlib import Path


def read_toml_file(file):
    """
    Read files in toml format
    """    
    return toml.load(file)

def relative_path(path):
    """
    Return the relative path of the project
    """
    return Path(__file__).parent.parent / path

def config_path():
    return  "/opt/iptables_tools"

def input_confirm(message=None):
    confirm = input(f'{message} [y/n]:')

    if confirm.lower() == 'y':
        return True
    else:
        return False

def all_project_path(name=None):
    """
    Return all path in the project
    """
    install_path = "/opt/iptables_tools"

    dirs = {
        'base': install_path,
        'export': f"{install_path}/export",
        'config-active': f"{install_path}/config-active.d",
        'config-available': f"{install_path}/config-available.d",
        'backup': f"{install_path}/backup",
    }

    if name:
        return dirs.get(name)

    return dirs

def all_project_files(name=None):
    """
    Return all files in the project
    """
    files = {
        'src_service': relative_path('systemd/iptables-tools.service'),
        'dst_service': '/etc/systemd/system/iptables-tools.service',
        'src_default': relative_path('templates/default.toml'),
        'active_default': f'{all_project_path("config-active")}/default.toml',
        'dst_default': f'{all_project_path("config-available")}/default.toml',
        'bkp_rules_v4': f'{all_project_path("backup")}/rules.v4',
        'bkp_rules_v6': f'{all_project_path("backup")}/rules.v6',
        'exp_rules_v4': f'{all_project_path("export")}/rules.v4',
        'exp_rules_v6': f'{all_project_path("export")}/rules.v6',
    }

    if name:
        return files.get(name)

    return files
    