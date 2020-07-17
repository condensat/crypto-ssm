from flask import Flask

from flask_jsonrpc import JSONRPC

# Flask application
app = Flask(__name__)

# Flask-JSONRPC
jsonrpc = JSONRPC(app, '/api/v1', enable_web_browsable_api=False)

@jsonrpc.method('new_master')
def new_master(entropy: str) -> dict:
  return {"entropy": entropy}

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
