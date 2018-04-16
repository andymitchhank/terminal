[![Build Status](https://api.travis-ci.org/whoopapps/terminal.svg?branch=master)](https://travis-ci.org/whoopapps/terminal)


# Terminal

A simple terminal web application built on React, Flask, and Click.

## Running

Okay, this is more complicated now, but shouldn't be too bad.

1. Install [Nanobox](https://docs.nanobox.io/install/). You'll probably have to make an account. You will need the credentials later.
2. `cd` into repo
3. Run `nanobox dns add local terminal.local`
5. Open another shell. You need two. You can use tmux or something if you prefer.
6. Run `nanobox evar add local IS_DEV=1`
7. Run `nanobox run` in both shells. Wait for the first to finish before running in the second. It will drop you into the container.
8. Run `cd /app/react_app && npm install && npm start` in the second. During dev, you may have to restart this. It sometimes hangs while file listening.
9. Run `cd /app/flask_app && gunicorn --bind 0.0.0.0:5000 -k flask_sockets.worker app:app` in the shell 1.
10. Navigate to terminal.local:5000 in a browser. 
11. Dev and restart commands as necessary.


## Notes

* The react app runs on port 3000
* The flask app runs on port 5000
* The flask app proxies requests to the react app during development. For production, the react app is built and served up directly by the flask app.
* The IS_DEV environment variable triggers the proxy instead of serving the build. If you keep getting a 404, make sure this is set and the react app is running. 
* I'm hoping to automate this a little more. I know it's tedious right now. 

