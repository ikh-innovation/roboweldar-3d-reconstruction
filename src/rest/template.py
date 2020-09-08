# 'images' and 'meshFiles' folders
#   are needed alongside this script
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
httpPort = "3000"
wsPort = "3001"

def connectWS(endpoint, host):
  wsClient = ws_client.getClient('ws://' + host + ':' + wsPort + '/' + endpoint)
  wst = threading.Thread(target=wsClient.run_forever)
  wst.daemon = True
  wst.start()
  running = True
  time.sleep(2)
  try:
    while (running):
      if (endpoint == 'sfm' ):
        val = 5
      else:
        val = 15
      message = json.dumps( { 'status': val } )
      ws_client.send_message(wsClient, message)
      time.sleep(1)

  except KeyboardInterrupt:
    running = False

# endpoint either 'cache_images'
# or 'cache_mesh'
def sendDummyFiles(endpoint, host):
  #dummy data, files with those names should exist in this dir 
  if (endpoint == 'cache_images'):
    filesNames = listdir('./images')
    files = map( lambda fileName: './images/' + fileName, filesNames )
  elif (endpoint == 'cache_mesh'):
    filesNames = listdir('./meshFiles')
    files = map( lambda fileName: './meshFiles/' + fileName, filesNames )
  http_client.send_images('http://' + host + ':' + httpPort + '/' + endpoint, files)

# obj upload example (mesh)
# e.g. sendMesh('mesh.obj')
def sendMesh(fName):
  http_client.uploadMesh('http://' + host + ':' + httpPort + '/cache_mesh', fName)

def getImages():
  images = http_client.getImageNames( 'http://' + host + ':' + httpPort + '/' + 'image_names' )
  for image in images:
    url = 'http://' + host + ':' + httPort + '/serve_image?name=' + image
    content = http_client.downloadImage(url)
    with open( str(image), 'wb') as f:
      f.write( content )

def runMe():
  if (len(sys.argv) < 4):
    print("wrong number of arguments")
    return
  host = sys.argv[1]
  if (sys.argv[2] == 'ws'):
    thisModuleHeader = sys.argv[3]
    connectWS(thisModuleHeader, host)
  elif (sys.argv[2] == 'http'):
    thisModuleFileEndpoint = sys.argv[3]
    sendDummyFiles(thisModuleFileEndpoint, host)

if __name__ == '__main__':
  runMe()


