CODE = app bootstrap django_app storage utils
WORKING_CODE = app/repositories app/schemas app/tests app/ws_consumers/mixins \
	app/schemas/ \
	app/ws_consumers/lobby_consumer_base.py \
	app/ws_consumers/lobby_consumer.py \
	app/card_abilities/cards/ \
	app/card_abilities/card_utils.py \
	app/admin/ \
	app/tasks.py \
	app/battle_service.py \
	app/ws_consumers/battle_consumer.py \
	app/services/ \
	app/models/ \
	app/apps.py

TEST = pytest app/tests --verbosity=2 --strict-markers ${arg} -k "${k}"

.PHONY: lint
lint:
	flake8 --jobs 4 --statistics --show-source $(CODE)
	pylint --jobs 4 $(CODE)
	black --check $(CODE)

.PHONY: lint_good_code
lint_good_code:
	flake8 --jobs 4 --statistics --show-source $(WORKING_CODE)
	pylint --jobs 4 $(WORKING_CODE)
	black --check $(CODE)

.PHONY: check_no_missing_migrations
check_no_missing_migrations:
	python manage.py makemigrations --check --dry-run

.PHONY: format
format:
	autoflake $(CODE)
	isort $(CODE)
	black --target-version py39 --skip-string-normalization $(CODE)
	unify --in-place --recursive $(CODE)

.PHONY: check
check: format test check_no_missing_migrations lint

.PHONY: check_good_code
check_good_code: format lint_good_code check_no_missing_migrations test

.PHONY: check_ci_job
check_ci_job: lint_good_code check_no_missing_migrations test

.PHONY: test
test:
	${TEST} --cov

.PHONY: test-fast
test-fast:
	${TEST} --exitfirst

.PHONY: test-failed
test-failed:
	${TEST} --last-failed
