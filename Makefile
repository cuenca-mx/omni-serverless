define USAGE
Super awesome hand-crafted build system ⚙️

Commands:
	init     		Install Python dependencies with pipenv
	test     		Run linters, test db migrations and tests.
	serve    		Run app in dev environment (localhost:3000).
	invoke   		Invoke function with event.json as an input
	new-bucket MY_BUCKET    Create S3 bucket
	package MY_BUCKET   	Package Lambda function and upload to S3
	deploy MY_BUCKET   	Deploy SAM template as a CloudFormation stack
endef

export USAGE

PIPENV := pipenv

help:
	@echo "$$USAGE"

install-pipenv:
	pip3 install pipenv --user


check-pipenv:
	$(foreach bin,$(PIPENV),\
    	$(if $(shell command -v $(bin) 2> /dev/null),$(info Found `$(bin)`),$(error Install `$(bin)` or add in PATH)))

init: install-pipenv check-pipenv
	pipenv install pytest pytest-mock
	pipenv install -r */requirements.txt

test: check-pipenv
	pipenv run python -m pytest tests/ -v

build:
	sam build

serve: build
	sam local start-api -p 3001

invoke: build
	sam local invoke CuencaShippingFunction --event event.json

new-bucket:
	aws s3 mb s3://$(filter-out $@,$(MAKECMDGOALS))

package: build
	sam package \
    --output-template-file packaged.yaml \
    --s3-bucket $(filter-out $@,$(MAKECMDGOALS))

deploy:
	sam deploy \
    --template-file packaged.yaml \
    --stack-name omni-serverless \
    --capabilities CAPABILITY_IAM