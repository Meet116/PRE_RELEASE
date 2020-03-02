#!/bin/bash

function main()
{
	for i in $@
	do
		case $i in
			--go_server_backup )
	  		shift
	  		go_server_backup $@
	  		;;
			--go_server_restore )
	  		shift
	  		go_server_restore $@
	  		;;
			--go_agent_reinstall )
				shift
				go_agent_reinstall
				;;
			-h | --help )
				echo "Usage Options are"
				echo "--go_server_backup					To take the gocd server backup."
				echo "--go_server_restore					To restore the gocd server."
				echo "--go_agent_reinstall					To restore the gocd agent."
				;;
			* )
				echo "Unknown optiondo "
				echo " -h or --help      To know the valid option"
				;;
		esac
	done
}


function go_server_backup()
{
	#Merge the code of go -server backup
	echo "go-server-backup $current_version $backup_version"
}

function go_server_restore()
{
	#To restore the go-server parameters to be passed are bucket name, server backup date, AWS access key and AWS secret key.
  service go-server stop
  BUCKET_NAME=$1
  SERVER_BACKUP_DATE=$2
  AWS_ACCESS_KEY=$3
  AWS_SECRET_KEY=$4
  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY aws s3 cp s3://$BUCKET_NAME/go-server/serrver-backup/$SERVER_BACKUP_DATE  /var/lib/gocd/backup/ --recursive
  current_version=$(dpkg -l go-server | grep -E -o '[0-9]+.[0-9]+.[0-9]+' | head -1)
  backup_version=$(cat /var/lib/go-server/artifacts/serverBackups/backup_20200227-173849/version.txt | grep -E -o '[0-9]+.[0-9]+.[0-9]+' | head -1)
  if $current_version != $backup_version
  then
  	echo " Please update the gocd version to $backup_version to perform backups."
  	exit 1
  fi 	
  export SERVER_INSTALLATION_DIR=/var/lib/go-server
  unzip db.zip -d $SERVER_INSTALLATION_DIR/db/h2db
  chown -R go:go /etc/go
  chown -R go:go /usr/share/go-server/wrapper-config
  chown -R go:go $SERVER_INSTALLATION_DIR/db/config.git
  mkdir -p /var/lib/go-server/run
  chown -R go:go /var/lib/go-server/run
  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY aws s3 cp s3://${BACKUP_BUCKET}/go-server/server-backup/plugins/external/  /var/lib/go-server/plugins/external/ --recursive
  chown -R go:go /var/lib/go-server/plugins/external
  service go-server restart
}


function go_agent_reinstall()
{
	#To remove and install the go-agent.
	service go-agent stop
	echo "deb https://download.gocd.org /" | sudo tee /etc/apt/sources.list.d/gocd.list
	apt-get purge -y go-agent
	rm -rf /var/log/go-agent/*
	rm -rf /var/lib/go-agent/*
	apt-get install -y go-agent
	service go-agent start
}

main "$@"