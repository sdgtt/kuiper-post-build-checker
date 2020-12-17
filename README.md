# kuiper-post-build-checker

A post boot configuration checker using pytest-testinfra to validate wether required packages, files and services are configured properly.

It automatically clones/pull ADI KUIPER GEN repo and checks needed files to counter
check with target configurations.**

This is work-in-progress, current supported checking:
1. Files
    * passwd
        * root (checks if root is present)
        * analog (checks if analog is present)
    * bashrc (checks if PYTHONPATH was set)
2. apt packages
    * stage4/00-install-packages/00-packages
    * stage4/00-install-packages/00-packages-nr
    * stage4/00-install-packages/01-packages
    * stage4/00-install-packages/02-packages
    * stage6/01-install-packages/00-packages
3. services (Services for now are specified manually in config.yaml)
    * iiod
    * sshd



**Please check config.yaml for details.

**Installation**

`$ git clone https://gitlab.analog.com/KPaller/sqa_post_boot_checker.git`

**Pre-requisites**

`$pip install -r requirements.txt`

**Configuration**

Modify config.yaml

1. Set host (multiple host allowed)
```
    # format: "paramiko://username:password@target_ip"
    testinfra:
      hosts:
        - "paramiko://analog:analog@192.168.1.113"
        - "paramiko://pi:raspberry@192.168.1.112"
```

2. Define files that contains packages list (currently supported format).
   Check **https://github.com/analogdevicesinc/adi-kuiper-gen** for directory structure.
```
    packages:
      paths:
        files:
          - stage4/00-install-packages/00-packages
          - stage4/00-install-packages/00-packages-nr
          - stage4/00-install-packages/01-packages
          - stage4/00-install-packages/02-packages
          - stage6/01-install-packages/00-packages
```

3. Define services that needs to be checked.
```
    services:
      default:
        - iiod
        - sshd
```


**Usage**

`$cd <working_path>`


( Clones/Pull Kuiper Gen and execute all test in test/*)

`$invoke test`


( Clones/Pull Kuiper Gen and checkout to specified tree (branch or commit)  and execute all test in test/*)

`$invoke test -t <branch/commit hash>`


( Clones/Pull Kuiper Gen and  execute test spicifed by test file)

`$invoke test -f <test file>`

( Clones/Pull Kuiper Gen and checkout to tree (branch or commit) specified )

`$invoke fetchkuipergen -t <branch/commit hash`

**Additional Notes**

Current functionality is tested using RPI running Kuiper RC5.





