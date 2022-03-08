
.PHONY: workflow-build
workflow-build: build-html 

.PHONY: build-lang
build-lang:
		docker run --rm -e GITHUB_TOKEN $(shell docker build . -q -f Dockerfile-addlanguage -t build-lang)

.PHONY: build-html
build-html:
		docker run --rm -e GITHUB_TOKEN $(shell docker build . -q -f Dockerfile-buildhtml -t build-html) 

.PHONY: build-translate
build-translate:
		docker build . -f Dockerfile-translate -t build-translate

.PHONY: build-geoip
build-geoip:
		docker build . -f Dockerfile-geoip -t build-geoip




		

