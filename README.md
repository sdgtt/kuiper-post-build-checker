# sqa_post_boot_checker

A post boot configuration checker using pytest-testinfra to make sure required packages, files and services are configured properly.
This is work-in-progress, current supported checking:
1. passwd file
    * root
    * analog
2. bashrc file
3. apt packages
    * adi-kuiper-gen/stage6/01-install-packages/00-packages
4. services
    *  iiod

**Installation**

`$ git clone https://gitlab.analog.com/KPaller/sqa_post_boot_checker.git`

**Pre-requisites**

Install pytest-testinfra

`$ pip3 install pytest-testinfra`

Install paramiko ( used as default backend )

`$ pip3 install paramiko`

**Execution**

`$pytest --hosts=root@<target_host> --sudo -v`

Example

`$pytest --hosts=root@192.168.10.56 --sudo -v` 

(This may asks for target host authorization for a number of times. To prevent that, refer to 'Configure ssh')

**Configure ssh**

1. Generate Key

`$ssh-keygen (This installs ssh key to default location. Specify passphrase)`

2. Copy public key target host
```
$ssh-copy <target_host>
ex. $ssh-copy-id 192.168.10.56
```


3. Use ssh-agent to prevent being ask of passphrase in each execution.
```
$eval `ssh-agent -s`
$ssh-add /root/.ssh/id_rsa (specify generated ssh key)
```





