db:
	docker run -d --name $$DBNAME -e POSTGRES_PASSWORD=$$POSTGRES_PASSWORD postgres:13.6
	direnv reload

psql:
	docker exec -it $$DBNAME psql -U postgres

start-docker:
	docker start $$DBNAME
	direnv reload

run:
	flask run

bin/git-bug:
	mkdir -p `dirname $@`
	wget https://github.com/MichaelMure/git-bug/releases/download/v0.8.0/git-bug_linux_amd64
	mv git-bug_linux_amd64 $@
	chmod +x $@

receiver:
	# run hook receiver
	FLASK_DEBUG=1 FLASK_APP=receiver flask run -p 5001
