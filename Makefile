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

kust-secrets.env: kust-secrets.tmp.env
	cat $< | DB_IP=$(shell cd $$TF_DIR && terraform output -raw db_private_ip) envsubst > $@

helm.yaml: helm.tmp.yaml tags.env
	cat $< | envsubst > $@

kustomize: kust-secrets.env secrets.env
	kubectl apply -k .

deploy-vars:
	# print the vars you need for a deploy
	# helm.tmp.yaml
	@cat helm.tmp.yaml | xargs -n 1 envsubst -v
	@echo
	# kust-secrets.tmp.env
	@cat kust-secrets.tmp.env | xargs -n 1 envsubst -v | grep -v DB_IP

helm-upgrade: helm.yaml
	helm upgrade --install -f $< task-inbox ./helm

.PHONY: webpushkeys
webpushkeys:
	# note: you have to also manually add a claims.json in this dir or `make kustomize` will fail
	mkdir -p $@
	# note: vapid will create keys if missing, check them otherwise (I think)
	cd $@ && vapid && vapid --applicationServerKey | awk '{print $$5}' | sed '/^$$/d' > applicationServerKey.b64
