#!/usr/bin/env python3

from base64             import b64decode
from tkinter            import Tk, Label
from PIL                import Image, ImageTk
from io                 import BytesIO

from pp_sslproto        import proto_ssl_image

#-------------------------------------------------

def get_image():
        buff = open('image.ack','rb').read()
        buff = buff.decode().encode('gb18030')
        image = proto_ssl_image({}).parse_image_ack(buff)['image']
        image = b64decode(image)
        return image

def show_photo(image):
        root  = Tk()
        root.title('Image')
        label = Label()
        photo = ImageTk.PhotoImage(Image.open(BytesIO(image)))
        label.configure(image = photo)
        label.pack()
        root.mainloop()

#-------------------------------------------------

if __name__ == '__main__' :
        show_photo(get_image())

