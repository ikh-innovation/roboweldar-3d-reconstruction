 #https://pypi.org/project/requests/2.7.0/
import requests, json

# host should be like "http://localhost:3000/cache_images
# imagesPathArr like ["/path/to/image1", "path/to/image2", ...]
# maybe change names to custom ones, e.g. file1.jpg
def send_images(host, imagesPathArr):
  files = []
  for index, imagePath in enumerate(imagesPathArr):
    openedFile = open(imagePath, 'rb')
    files.append(('files', (openedFile.name, openedFile)))

  r = requests.post(host, files=files)

def getImageNames(link):
  r = requests.get(link)
  if (r.status_code == 200):
    names = json.loads(r.text)
    return names
  else:
    print( 'request not served correctly', r)
    
def downloadImage(link):
  r = requests.get(link)
  if (r.status_code == 200):
    return r.content
  else:
    print( 'request not served correctly', r)

def uploadMesh(link, meshFilePath):
  openedFile = open(meshFilePath, 'rb')
  files = [('files', (openedFile.name, openedFile))]
  r = requests.post(link, files=files)
