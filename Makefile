### dev/env ops ###############################################################

env.update:
	pip install -r requirements/requirements.txt

env.update.all:
	pip install -r requirements/requirements.txt
	pip install -r requirements/requirements-test.txt
	pip install -r requirements/requirements-dev.txt

env.jupyter:
	ipython kernel install --name "finx-all" --user

test:
	pytest .

todo:
	grep -irn todo .


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
