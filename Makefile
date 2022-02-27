download:
	@python cli.py download --report-name=annual

download.daily:
	@python cli.py download --report-name=daily --cache

download.weekly:
	@python cli.py download --report-name=weekly --cache



### dev/env ops ###############################################################

env.update:
	pip install -r requirements.txt

env.update.all:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install -r requirements-dev.txt

env.jupyter:
	ipython kernel install --name "finx-all" --user

test:
	pytest .

changelog:
	git-chglog -o CHANGELOG.md

changelog.commit: changelog
	git add CHANGELOG.md && git commit CHANGELOG.md -m "update changelog"



### release ###################################################################

release: release.applytag release.check release.build release.upload

release.applytag:
	echo $$(git describe --tags --abbrev=0 ) > finx_ib_reports/version.txt

release.check:
	pre-commit run -a
	git diff --quiet

release.build:
	python setup.py sdist bdist_wheel

release.upload:
	twine upload dist/*
