# sqa_post_boot_checker

A post boot configuration checker using pytest-testinfra to validate wether required packages, files and services are configured properly.
This is work-in-progress, current supported checking:
1. Files
    * passwd
        * root
        * analog
    * bashrc
2. apt packages
    * stage4/00-install-packages/00-packages
    * stage4/00-install-packages/00-packages-nr
    * stage4/00-install-packages/01-packages
    * stage4/00-install-packages/02-packages
    * stage6/01-install-packages/00-packages
3. services
    * iiod
    * sshd

Please check config.yaml for configurations.

**Installation**

`$ git clone https://gitlab.analog.com/KPaller/sqa_post_boot_checker.git`

**Pre-requisites**

`$pip install -r requirements.txt`

**Configuration**

Modify config.yaml

**Usage**

`$cd <working_path>`





