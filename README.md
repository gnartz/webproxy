# webproxy
A simple but functional async web proxy.

## install
pip install gnartz_webproxy

## usage
    > webproxy --help
    Usage: webproxy [OPTIONS]
    
    Options:
      --host TEXT     Host.  [default: 0.0.0.0]
      --port INTEGER  Port.  [default: 8080]
      --cert TEXT     SSL cert.
      --key TEXT      SSL key.
      --target TEXT   Proxy target url  [required]
      --help          Show this message and exit.
