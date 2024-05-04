# Iptables Tools

Iptables Tools é uma biblioteca Python que abstrai os comandos do iptables, permitindo que os usuários criem suas regras de firewall sem precisar conhecer os comandos do iptables.

### Requisitos
- Python 3.10+ (Testado com Python 3.10.0), mas deve funcionar com versões anteriores do Python 3
- iptables
- ip6tables

### Instalação
Para instalar a biblioteca Iptables Tools, você pode usar o pip:
```
pip install iptables-tools
iptables-tools install
```

Obs: A instalação criará um backup das regras atuais do iptables e ip6tables na pasta `/opt/iptables_tools/backup/`, em caso de problemas, você pode restaurar as regras usando o comando `iptables-tools roolback`.

#### Configuração de regras

Para usar a biblioteca Iptables Tools, você precisará criar um arquivo de configuração TOML com suas regras de firewall na pasta `/opt/iptables_tools/config-available.d/`. A biblioteca lerá este arquivo e adicionará as regras ao iptables.

Aqui está um exemplo de como um arquivo de configuração para ssh pode parecer:
```
cat /opt/iptables_tools/config-available.d/ssh.toml

[ssh] # Esta seção define a configuração para o serviço SSH. O usuário pode alterar conforme necessário.

[ssh.input] # Esta seção define o protocolo, a chain e a porta conforme necessário.
protocol = "tcp"
chain = "INPUT"
port = 22

[ssh.input.ipv4.accept] # Esta seção define as regras de aceitação para IPv4.
mapping = [
    {src='127.0.1.1', dst='127.0.0.1', comment='Permitir acesso de rede IPv4 específica'},
]

[ssh.input.ipv4.drop] # Esta seção define as regras de rejeição para IPv4.
mapping = [
    {comment='Bloqueia SSH IPv4'}
]

[ssh.input.ipv6.accept] # Esta seção define as regras de aceitação para IPv6.
mapping = [
    {src='2001:db8:ca5a:faca::/64', comment='Permitir acesso de rede IPv6 específica'},
]

[ssh.input.ipv6.drop] # Esta seção define as regras de rejeição para IPv4.
mapping = [
    {comment='Bloqueia SSH IPv6'}
]

# Cada regra de mapping é um dicionário que pode conter as chaves src (para a rede de origem), dst (para a rede de destino) e comment (para um comentário descritivo). A ausencia de src ou dst significa que a regra se aplica a qualquer origem ou destino.
```

O resultado final será algo como:
```
iptables -A INPUT -s 127.0.1.1/32 -d 127.0.0.1/32 -p tcp -m tcp --dport 22 -m comment --comment "Permitir acesso de rede IPv4 específica" -j ACCEPT
iptables -A INPUT -p tcp -m tcp --dport 22 -m comment --comment "Bloqueia SSH IPv4" -j DROP
ip6tables -A INPUT -s 2001:db8:ca5a:faca::/64 -p tcp -m tcp --dport 22 -m comment --comment "Permitir acesso de rede IPv6 específica" -j ACCEPT
ip6tables -A INPUT -p tcp -m tcp --dport 22 -m comment --comment "Bloqueia SSH IPv6" -j DROP
```

#### Adicionando mais regras
Para adicionar mais regras, basta adicionar o dicionário de configuração no arquivo TOML, exemplo:

```
[ssh.input.ipv4.accept] # Esta seção define as regras de aceitação para IPv4.
mapping = [
    {src='127.0.1.1', dst='127.0.0.1', comment='Permitir acesso de rede 127 IPv4 específica'},
    {src='10.10.10.1', comment='Permitir acesso de rede 10 IPv4 específica'},
]
```

O resultado final será algo como:
```
iptables -A INPUT -s 127.0.1.1/32 -d 127.0.0.1/32 -p tcp -m tcp --dport 22 -m comment --comment "Permitir acesso de rede 127 IPv4 específica" -j ACCEPT
iptables -A INPUT -s 10.10.10.1/32 -p tcp -m tcp --dport 22 -m comment --comment "Permitir acesso de rede 10 IPv4 específica" -j ACCEPT
```

### Iniciando o serviço
Para iniciar o serviço, você pode usar o comando:
```
systemctl start iptables-tools
```
Obs: Após iniciar o serviço irá adicionar as regras de firewall ao iptables.

### Verificando o status do serviço
Para verificar o status do serviço, você pode usar o comando:
```
systemctl status iptables-tools
```

### Parando o serviço
Para parar o serviço, você pode usar o comando:
```
systemctl stop iptables-tools
```
OBs: Após parar o serviço irá remover as regras de firewall do iptables.

### Reiniciando o serviço
Para reiniciar o serviço, você pode usar o comando:
```
systemctl restart iptables-tools
```
