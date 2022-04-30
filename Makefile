server:
	python3 -m nuitka --standalone --onefile --follow-imports --include-data-dir=src/main/python/resources/=resources/ --linux-onefile-icon=src/main/python/resources/saoirse/media/imags/saoirse_logo.png src/main/python/saoirse_server.py

client:
	python3 -m nuitka --standalone --onefile --enable-plugin=tk-inter,numpy --follow-imports --include-data-dir=src/main/python/resources/=resources/ --linux-onefile-icon=src/main/python/resources/saoirse/media/images/saoirse_logo.png src/main/python/saoirse_client.py
