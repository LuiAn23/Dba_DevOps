Del servidor de producción pasar los siguientes war y desplegar (la ultima version, por fecha):

scp renovacion2.0.war renonacional.formulario-1.0.8.war renonacional.firma-1.0.1.war renonacional.descarga-1.0.0.war renonacional.pago-1.0.2.war dominios.ws-2.1.0.war sisadmin@192.168.201.239:/tmp




Desplegar en ambiente de Calidad los siguientes war, estos se deben tomar de la ruta: /u01/deploy del servidor del servidor de weblogic 14: 192.168.201.139

renovacion_pnf2.0

renonacional.formulario:pnf 

renonacional.firma_pnf

renonacional.descarga_pnf

renonacional.pago_pnf

dominios.ws_pnf.2.0

scp renovacion_pnf2.0.war renonacional.formulario_pnf-1.0.0.war renonacional.firma_pnf-1.0.0.war renonacional.descarga_pnf-1.0.0.war renonacional.pago_pnf-1.0.0.war dominios.ws_pnf-2.1.0.war  sisadmin@192.168.201.239:/tmp



COCLOCCCTST03 - 192.168.201.233
COCLOCCCTST06 - 192.168.201.236
COCLOCCCTST09 - 192.168.201.239 
COCLOCCCTST11 - 192.168.201.241
COCLOCCCTST15 - 192.168.201.251


#################### ACTIVAR PUERTOS ################

[root@cocloccctstl09 ~]# systemctl start firewalld
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# firewall-cmd --permanent --add-port=1821/tcp
success
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# firewall-cmd --reload
success
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# systemctl status firewalld
● firewalld.service - firewalld - dynamic firewall daemon
     Loaded: loaded (/usr/lib/systemd/system/firewalld.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-02-12 12:09:35 -05; 33s ago
       Docs: man:firewalld(1)
   Main PID: 19724 (firewalld)
      Tasks: 3 (limit: 150624)
     Memory: 32.6M
        CPU: 863ms
     CGroup: /system.slice/firewalld.service
             └─19724 /usr/bin/python3 -s /usr/sbin/firewalld --nofork --nopid

Feb 12 12:09:35 cocloccctstl09 systemd[1]: Starting firewalld - dynamic firewall daemon...
Feb 12 12:09:35 cocloccctstl09 systemd[1]: Started firewalld - dynamic firewall daemon.
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# firewall-cmd --list-ports
7001/tcp
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 
[root@cocloccctstl09 ~]# 


[root@cocloccctstl41 bin]#   

firewall-cmd --permanent --add-port=4848/tcp  
firewall-cmd --permanent --add-port=8686/tcp  
firewall-cmd --permanent --add-port=6666/tcp  
firewall-cmd --permanent --add-port=8080/tcp  
firewall-cmd --permanent --add-port=8443/tcp  
firewall-cmd --reload
