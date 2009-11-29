
first:
	@echo "Make what?"

erase-databases:
	mysql ldreg < recreate.sql

