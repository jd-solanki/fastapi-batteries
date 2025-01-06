ex:
	uvicorn $$(echo $(path) | cut -f1 -d '.' | sed 's/\//./g'):app --reload --port 7000