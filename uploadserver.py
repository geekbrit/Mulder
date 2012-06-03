import cgi
import sys
import os
import shutil
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading

FILES = os.path.dirname(os.path.realpath(__file__)) + '/files/'
F640  = os.path.dirname(os.path.realpath(__file__)) + '/files640/'

class IM_Thread( threading.Thread ):
    def __init__( self, filename ):
        self.fn = filename
        threading.Thread.__init__ ( self )

    def run( self ):
        global FILES
        global F640
        shutil.copy( FILES + self.fn, F640 + self.fn )
        os.system( "mogrify -strip -resize \"640x640>\" %s" % F640 + self.fn )
        os.system( "mogrify -gravity Center -extent 640x640 %s" % F640 + self.fn )



# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

class MainHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global FILES

        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))


            if ctype == 'multipart/form-data':
                fss = cgi.FieldStorage( fp = self.rfile,
                                       headers = self.headers,
                                       environ = {'REQUEST_METHOD':'POST'}
                                     )
            else: raise Exception('Unexpected POST request')

                        

            #print repr(fss['qqfile'])
             
            for fs in fss['qqfile']:
                #print repr(fs)

                filename = os.path.basename(fs.filename)

                if '' == filename:
                    continue
    
                fullname = FILES + filename

                if not os.path.exists(fullname):
                     with open(fullname, 'wb', 10000) as o:
                         for chunk in fbuffer(fs.file):
                            o.write( chunk )
                         o.close()

                IM_Thread(filename).start()
                     
            self.send_response(200)
            self.end_headers()
            self.wfile.write('{"success":true}');

        except Exception as e:
            print e
            self.send_error(500,'POST to "%s" failed: %s' % (self.path, str(e)) )
 
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('{"success":true}');

def main():
    try:
        server = HTTPServer(('', 11999), MainHandler)
        print 'started httpserver...'
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
 
