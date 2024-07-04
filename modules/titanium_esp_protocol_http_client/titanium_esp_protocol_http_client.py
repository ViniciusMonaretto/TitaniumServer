import tornado.ioloop
import tornado.httpclient
import asyncio

class TitaniumEspProtocol:
    def __init__(self):
        self._stop = False
        self._url = "http://192.168.0.13/get_area?id=1"
        self._error = 0

    async def run(self):
       http_client = tornado.httpclient.AsyncHTTPClient()
       while not self._stop:
            try:
                response = await http_client.fetch(self._url)
                print("Response {} error count {}".format(response.body, self._error))
            except Exception as e:
                print(e)
                self._error = self._error + 1
                pass
            await asyncio.sleep(1)