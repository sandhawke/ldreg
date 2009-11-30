
first:
	@echo "Make what?"

erase-databases:
	for suffix in tracker_1 tracker_2 scanner_1 scanner_2 client; do mysql ldreg_$$suffix < recreate.sql ; done


