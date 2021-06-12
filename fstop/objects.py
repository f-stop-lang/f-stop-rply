from rply.token import BaseBox

class ImageRepr(BaseBox):

    def __init__(self, image):
        self.image = image
    
    def __repr__(self):
        return "<ImageRepr image='%s'>" % self.image