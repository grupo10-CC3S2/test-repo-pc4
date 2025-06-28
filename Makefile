setup:
	docker build -t timeserver:latest app
	kubectl cluster-info
	kubectl apply -f k8s/
	kubectl get pods

teardown:
	kubectl delete -f k8s/
	docker image rm timeserver
