import websocket, re

def on_message(ws, message):
  if (re.search("photo_capture", ws.header[0])):
      # process
      # upload files to server (http)
      
      print("photo_capture related")
  elif (re.search("sfm", ws.header[0])):
      # get images url's from server (http)
      # get images from server (http)
      # process
      print("sfm related")

def on_error(ws, error):
  print(error)

def on_close(ws):
  print("connection closed")

def on_open(ws):
  print("connection opened")

# expects a serialized JSON object
# as message
def send_message(ws, message):
  ws.send(message)

# host should be like "ws://localhost:3001"
# customHeader either "photo_capture"
#  or "sfm"
def getClient(link):
  websocket.enableTrace(False)
  ws = websocket.WebSocketApp(link,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)
  return ws
