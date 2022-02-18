
.PHONY: workflow-build
workflow-build: build-html 

.PHONY: build-lang
build-lang:
		docker run --rm -e GITHUB_TOKEN -it $(shell docker build . -q -f Dockerfile-addlanguage -t build-lang)

.PHONY: build-html
build-html:
		docker run --rm -e GITHUB_TOKEN -it $(shell docker build . -q -f Dockerfile-buildhtml -t build-html) 


		

