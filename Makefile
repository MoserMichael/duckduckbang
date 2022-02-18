
.PHONY: workflow-build
workflow-build: build-html 

.PHONY: build-lang
build-lang:
		@docker build .  --build-arg GITHUB_TOKEN -f Dockerfile-addlanguage -t build-lang

.PHONY: build-html
build-html:
		@docker build .  -f Dockerfile-buildhtml -t build-html

