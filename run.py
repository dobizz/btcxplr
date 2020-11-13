#!/usr/bin/env python3
'''
This is the file that is invoked to start up a development server. It gets a copy of the app from your package and runs it. This won’t be used in production, but it will see a lot of mileage in development.
'''
from btcxplr import app

if __name__ == "__main__":
	DEV_HOST = "0.0.0.0"
	DEV_PORT = 5000
	app.run(DEV_HOST, DEV_PORT, debug=True)