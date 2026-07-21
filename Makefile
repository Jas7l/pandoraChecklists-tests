# Makefile для управления Allure отчетами

.PHONY: help allure-generate allure-serve allure-open allure-clean

help:
	@echo "Available commands:"
	@echo "  make allure-generate  - Generate Allure report from results"
	@echo "  make allure-serve     - Serve Allure report locally"
	@echo "  make allure-open      - Generate and open Allure report"
	@echo "  make allure-clean     - Clean Allure results and report directories"

allure-generate:
	@echo "Generating Allure report..."
	allure generate allure-results -o allure-report --clean
	@echo "✅ Report generated in allure-report/"

allure-serve:
	@echo "Serving Allure report..."
	allure serve allure-results

allure-open:
	@echo "Generating and opening Allure report..."
	allure generate allure-results -o allure-report --clean
	@echo "✅ Report generated"
	allure open allure-report

allure-clean:
	@echo "Cleaning Allure directories..."
	rm -rf allure-results
	rm -rf allure-report
	@echo "✅ Cleaned"

# Комбинированная команда: прогон тестов + генерация отчета
test-api-allure:
	@echo "Running API tests with Allure..."
	pytest -m api --alluredir=allure-results
	@echo "✅ Tests completed"
	make allure-generate

# Запуск тестов с генерацией отчета и открытием
test-api-allure-open:
	@echo "Running API tests with Allure..."
	pytest -m api --alluredir=allure-results
	@echo "✅ Tests completed"
	make allure-open