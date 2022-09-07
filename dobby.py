#!/usr/env python3
import http.server
import os
import logging
import io
import cgi
import socketserver

PORT=44444

try:
    import http.server as server
except ImportError:
  #Python 2.*
  import SimpleHTTPServer as server
  
class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
  
  #Handles POST requests
  def do_POST(self):
    r, info = self.deal_post_data()
    print(r, info, "by: ", self.client_address)
    f = io.BytesIO()
    if r:
      f.write(b"Success\n")
    else:
      f.write(b"Failed\n")
    length = f.tell()
    f.seek(0)
    self.send_response(200)
    self.send_header("Content-Type", "multipart/form-data")
    self.send_header("Content-Length", str(length))
    self.end_headers()
    if f:
      self.copyfile(f, self.wfile)
      f.close()
   
  def deal_post_data(self):
    ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
    pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
    if ctype == 'multipart/form-data':
      form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
      print (type(form))
      try:
        if isinstance(form["file"], list):
          for record in form["file"]:
            open("./%s"%record.filename, "wb").write(record.file.read())
        else:
            open("./%s"%form["file"].filename, "wb").write(form["file"].file.read())
      except IOError:
        return (False, "Cannot create file to write")
    return (True, "Uploaded Successfully")
        
  #Handles GET requests
  def do_GET(self):
    server.SimpleHTTPRequestHandler.do_GET(self)
    logging.warning(self.headers)
    
  #Handles PUT requests
  def do_PUT(self):
    filename = os.path.basename(self.path)
    
    #Don't overwrite files
    if os.path.exists(filename):
      self.send_response(409, 'Conflict')
      self.end_headers()
      reply_body = '"%s" already exists\n' % filename
      self.wfile.write(reply_body.encode('utf-8'))
      return
    
    file_length = int(self.headers['Content-Length'])
    with open(filename, 'wb') as output_file:
      output_file.write(self.rfile.read(file_length))
    self.send_response(201, 'Created')
    self.end_headers()
    reply_body = 'Saved "%s"\n' % filename
    self.wfile.write(reply_body.encode('utf-8'))
    
if __name__ == '__main__':
  server.test(HandlerClass=HTTPRequestHandler)

Handler - HTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
  print("serving at port", PORT)
  httpd.serve_forever()
