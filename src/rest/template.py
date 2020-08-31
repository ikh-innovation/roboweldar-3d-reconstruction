# args: 
#   localhost -> server hostname
#   ws/http -> ws (transmit data) or
#     http (post images)
# examples:
#   python2 template.py localhost ws photo_capture
#   python3 template.py localhost ws sfm
#   python2 template.py localhost http cache_images
#   python2 template.py localhost http cache_mesh

import ws_client, http_client, json, sys, threading, time
from os import listdir
host = "localhost"

def connectWS(endpoint):
  wsClient = ws_client.getClient("ws://" + host + ":3001/" + endpoint)
  wst = threading.Thread(target=wsClient.run_forever)
  wst.daemon = True
  wst.start()
  running = True
  time.sleep(5)
  try:
    while (running):
      message = '{ "pcStatus": 5 }'
      ws_client.send_message(wsClient, message)
      time.sleep(1)

  except KeyboardInterrupt:
    running = False

# endpoint either "cache_images"
# or "cache_mesh"
def sendDummyFiles(endpoint):
  #dummy data, files with those names should exist in this dir 
  if (endpoint == "cache_images"):
    files = ["image1.jpg", "image2.jpg", "image3.jpg"]
  elif (endpoint == "cache_mesh"):
    filesNames = listdir('./meshFiles')
    files = map( lambda fileName: './meshFiles/' + fileName, filesNames )
  http_client.send_images("http://" + host + ":3000/" + endpoint, files)

# obj upload example (mesh)
# e.g. sendMesh("mesh.obj")
def sendMesh(fName):
  http_client.uploadMesh("http://localhost:3000/cache_mesh", fName)

def getImages(host, path):
  images = http_client.getImageNames( "http://" + host + ":3000/" + 'image_names' )
  for image in images:
    url = "http://" + host + ":3000/serve_image?imageName=" + image
    content = http_client.downloadImage(url)
    with open( os.path.join(path, str(image)), 'wb') as f:
      f.write( content )

if __name__ == "__main__":
  host = sys.argv[1]
  if (sys.argv[2] == "ws"):
    thisModuleHeader = sys.argv[3]
    connectWS(thisModuleHeader)
  elif (sys.argv[2] == "http"):
    thisModuleFileEndpoint = sys.argv[3]
    sendDummyFiles(thisModuleFileEndpoint)
    

