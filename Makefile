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
