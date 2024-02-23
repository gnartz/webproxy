import ssl
import logging
import click
import aiohttp
from aiohttp.web import middleware


def make_url(request):
    url = f"{request.app['target']}{request.path_qs}"
    return url


async def connect_remote_websocket(request, proxied_ws):
    async with aiohttp.ClientSession() as session:
        url = make_url(request)
        async with session.ws_connect(url) as remote_ws:
            async for remote_msg in remote_ws:
                match remote_msg.type:
                    case aiohttp.WSMsgType.CLOSE:
                        await remote_ws.close()
                    case aiohttp.WSMsgType.TEXT:
                        await proxied_ws.send_str(remote_msg.data)
                    case aiohttp.WSMsgType.ERROR:
                        logging.error(ws.exception())


async def websocket_handler(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        match msg.type:
            case aiohttp.WSMsgType.CLOSE:
                await ws.close()
            case aiohttp.WSMsgType.TEXT:
                await connect_remote_websocket(request, ws)
            case aiohttp.WSMsgType.ERROR:
                logging.error(ws.exception())
    return ws


async def proxy_handler(request):
    async with aiohttp.ClientSession() as session:
        url = make_url(request)
        match request.method:
            case "GET":
                resp = await session.get(url, headers=request.headers)
            case "HEAD":
                resp = await session.head(url, headers=request.headers)
            case "OPTIONS":
                resp = await session.options(url, headers=request.headers)
            case "DELETE":
                resp = await session.delete(url, headers=request.headers)
            case "POST":
                resp = await session.post(url, data=request.content, headers=request.headers)
            case "PUT":
                resp = await session.put(url, data=request.content, headers=request.headers)
            case "PATCH":
                resp = await session.patch(url, data=request.content, headers=request.headers)
        return aiohttp.web.Response(status=resp.status, text=await resp.text(), headers=resp.headers)


@middleware
async def entry(request: aiohttp.ClientRequest, handler):
    rtn = aiohttp.web.Response(status=404, text="Not found.")
    try:
        upgrade = request.headers.get("Upgrade")
        if upgrade and upgrade == "websocket":
            rtn = await websocket_handler(request)
        else:
            rtn = await proxy_handler(request)
    except Exception as e:
        rtn = aiohttp.web.Response(status=500, text=f"ERROR -> {str(e)}")
        logging.error(str(e))
    return rtn


@click.command()
@click.option("--host", default="0.0.0.0", help="Host.", show_default=True)
@click.option("--port", default=8080, help="Port.", show_default=True)
@click.option("--cert", default=None, help="SSL cert.", show_default=True)
@click.option("--key", default=None, help="SSL key.", show_default=True)
@click.option("--target", help="Proxy target url", required=True)
def main(host, port, cert, key, target):
    logging.basicConfig(
        format="[%(asctime)s: %(levelname)s/%(threadName)s/%(funcName)s/%(lineno)d] %(message)s",
        level=logging.INFO
    )
    ctx = None
    if cert and key:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)

    app = aiohttp.web.Application(middlewares=[entry])
    app["target"] = target.rstrip("/")
    aiohttp.web.run_app(app, host=host, port=port, access_log=None, ssl_context=ctx)


if __name__ == "__main__":
    main()

