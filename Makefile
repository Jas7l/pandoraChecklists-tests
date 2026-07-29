.PHONY: help allure-generate allure-serve allure-clean

help:
	@echo "Available commands:"
	@echo "  make allure-generate  - Generate Allure report from results"
	@echo "  make allure-serve     - Serve Allure report locally"
	@echo "  make allure-clean     - Clean Allure results and report directories"

allure-generate:
	@echo "Generating Allure report..."
	allure generate allure-results -o allure-report --clean
	@echo "✅ Report generated in allure-report/"

allure-serve:
	@echo "Serving Allure report..."
	allure serve allure-results

allure-clean:
	@echo "Cleaning Allure directories..."
	rm -rf allure-results
	rm -rf allure-report
	@echo "✅ Cleaned"
