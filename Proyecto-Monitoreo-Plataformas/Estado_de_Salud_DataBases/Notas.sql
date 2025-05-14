


---- .116
ssh-copy-id sisadmin@192.168.202.2


Destino:

ssh-keygen -t rsa -b 2048
ssh-copy-id sisadmin@192.168.202.116







Docunet:

ip:192.168.202.2
listener: 1521

Filesystem:

[sisadmin@coclocccprdb02 ~]$ df -h   ############ FILESYSTEM
S.ficheros                         Tamaño Usados  Disp Uso% Montado en

/dev/mapper/rhel-Archivelog           50G   4,8G   46G  10% /Archivelog
/dev/mapper/rhel-u01                 100G    22G   79G  22% /u01
/dev/mapper/rhel-Data                600G   152G  448G  26% /Data
/dev/mapper/rhel-Backup              110G    75G   36G  68% /Backup
/dev/mapper/shreplexvg-shareplexvl    77G    23G   55G  30% /shareplex
10.80.5.2:CCCU07                     5,0T   4,1T  977G  81% /u07


MEMORIA:
CPU:

############## Validar instancia si dias de Actividad es menor a 1:


COLUMN INSTANCE_NAME FORMAT A20
COLUMN HOST_NAME FORMAT A25
COLUMN VERSION FORMAT A15
COLUMN STATUS FORMAT A10
COLUMN ARCHIVER FORMAT A10
COLUMN STARTUP_TIME FORMAT A20
COLUMN DIAS_DE_ACTIVIDAD FORMAT 999
SELECT 
    INSTANCE_NAME,
    HOST_NAME,
    VERSION,
    STATUS,
    ARCHIVER,
    TO_CHAR(STARTUP_TIME, 'DD-MON-YYYY HH24:MI:SS') AS STARTUP_TIME, 
    TRUNC(SYSDATE) - TRUNC(STARTUP_TIME) AS DIAS_DE_ACTIVIDAD
FROM 
    V$INSTANCE;


S.ACTIVAS mas de 4 horas en ejecuccion:


SELECT S.SID,
       S.SERIAL#,
       P.PID "ORAPID",
       P.SPID "SPID",
       S.USERNAME,
       S.STATUS,
       S.LAST_CALL_ET / 180 AS "TIME (MIN)",
       S.OSUSER,
       S.MACHINE,
       S.PROGRAM,
       S.ACTION
FROM gV$SESSION S, gV$PROCESS P
WHERE S.PADDR = P.ADDR
  AND S.USERNAME IS NOT NULL
  AND S.STATUS = 'ACTIVE'
ORDER BY S.LAST_CALL_ET ASC;  
/

s.NACTIVAS:

SELECT S.SID,
       S.SERIAL#,
       P.PID "ORAPID",
       P.SPID "SPID",
       S.USERNAME,
       S.STATUS,
       S.LAST_CALL_ET / 360 AS "TIME (MIN)",
       S.OSUSER,
       S.MACHINE,
       S.PROGRAM,
       S.ACTION
FROM gV$SESSION S, gV$PROCESS P
WHERE S.PADDR = P.ADDR
  AND S.USERNAME IS NOT NULL
  AND S.STATUS = 'INACTIVE'
ORDER BY S.LAST_CALL_ET ASC;  
/

############# Tablespaces Alertados:

SELECT COUNT(df.tablespace_name) "Nr of Tablespaces",LISTAGG (
DF.TABLESPACE_NAME
|| ' ==> '
|| (ROUND (100 * ( (DF.BYTES - TU.BYTES) / DF.MAXBYTES)))
|| '%',
CHR (10))
WITHIN GROUP (ORDER BY DF.TABLESPACE_NAME)
"PORCENTAJE USO %"
FROM ( SELECT TABLESPACE_NAME,
SUM (BYTES) BYTES,
SUM (DECODE (MAXBYTES, 0, BYTES, MAXBYTES)) MAXBYTES
FROM DBA_DATA_FILES
WHERE TABLESPACE_NAME NOT IN ('TSESB_CLOB_40M','UNDOTBS1')
GROUP BY TABLESPACE_NAME) DF,
( SELECT TABLESPACE_NAME, SUM (BYTES) BYTES
FROM DBA_FREE_SPACE
WHERE TABLESPACE_NAME NOT IN ('TSESB_CLOB_40M','UNDOTBS1')
GROUP BY TABLESPACE_NAME) TU
WHERE DF.TABLESPACE_NAME = TU.TABLESPACE_NAME
AND (ROUND (100 * ( (DF.BYTES - TU.BYTES) / DF.MAXBYTES)) > 92) ;



############## Validar finalizacion de los Backups STATUS: 

SET LINESIZE 200
SET PAGESIZE 100
COLUMN START_TIME FORMAT A20
COLUMN END_TIME FORMAT A20
COLUMN BACKUP_TYPE FORMAT A15
COLUMN STATUS FORMAT A10
COLUMN ELAPSED_TIME FORMAT A15
COLUMN BACKUP_SIZE_GB FORMAT A20
COLUMN OUTPUT_DEVICE FORMAT A20

SELECT INPUT_TYPE "BACKUP_TYPE",
       STATUS,
       TO_CHAR(START_TIME, 'MM/DD/YYYY:HH24:MI:SS') AS START_TIME,
       TO_CHAR(END_TIME, 'MM/DD/YYYY:HH24:MI:SS') AS END_TIME,
       TRUNC((ELAPSED_SECONDS/60), 2) "ELAPSED_TIME(Min)",
       TO_CHAR(ROUND(OUTPUT_BYTES/1024/1024/1024, 2), '99999999.99') "BACKUP_SIZE_GB",
       OUTPUT_DEVICE_TYPE "OUTPUT_DEVICE"
FROM V$RMAN_BACKUP_JOB_DETAILS
WHERE START_TIME > SYSDATE - 10
ORDER BY END_TIME DESC;


########## grep al alert de la BD:

grep "ORA-" /u01/app/oracle/diag/rdbms/docunet/DOCUNET/trace/alert_DOCUNET.log | grep -v -E "ORA-06550|ORA-12012"


########### objectos invalidos #####

validar Cantidad de determinados schemas. y colocar un archivo de excpeciones. 



SELECT owner, COUNT(*) AS invalid_objects
FROM dba_objects
WHERE status = 'INVALID'
GROUP BY owner;

########### Estados de los indices ############################


SQL> SELECT COUNT(*) AS unusable_indexes
FROM all_indexes
WHERE status = 'UNUSABLE';  2    3  

UNUSABLE_INDEXES
----------------
	       0

