# GOCD BACKUP AND RESTORE
- Switch to the root user to execute the go_backup_restore.sh script
- To take the go-server backup run the bellow command.
    ``` 
    ./go_backup_restore.sh --go_server_backup
    ``` 
    - Takes the backup and copy to the aws s3 bucket
- To restore the go-server run the below command.
    ```
    ./go_backup_restore.sh --go_server_restore <bucket-name> <server-backup-date> <AWS-access-key> <AWS-secret-key>
    ```
   - Pass the S3 bucket-name, Server-backup-date, AWS-access-key and AWS-secret-key .
   - Stops the gocd-server.
   - Copy the backup file from AWS S3 bucket and plugins from AWS S3 bucket.
   - Restart the gocd-server
- To reinstall the go-agent run teh below command.
    ```
    ./go_backup_restore.sh --go_agent_reinstall
    ```
    - Stops the gocd-agent.
    - Purge the gocd-agent.
    - Install teh gocd-agent.
    - Restart the gocd-agent.