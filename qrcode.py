#!/usr/bin/env python

# Encode:

#   Name: 15 chars (total 21)
#   IP No: F 7 letters (total 16)
#   Diagnosis: 16 letters (total 27)
#   date of procedure: 10 (total 29)

#   total - 93



from PyQRNative import QRCode, QRErrorCorrectLevel

class QRImg():
    def __init__(self, data_list, img_path):
        """
        data_list is a list of 2-tuples,
        items of tuple are field and its value.
        about four items will fit in
        img_path is path where image should be written
        """
        self.img_path = img_path
        #self.data = self.dict2data(data_dict)
        self.data = self.lst2str(data_list)

        
    def make_image(self):
        qr = QRCode(8, QRErrorCorrectLevel.L) # 8 handles long data also
        qr.addData(self.data)
        qr.make() # todo: handle typeerror when data is too large

        im = qr.makeImage()

        im.show()
        
        im.save(self.img_path, "JPEG")
        

    def lst2str(self, lst):
        """
        Given a list of two-tuples, return
        string.
        First item in tuple will always be a string
        >>> lst2str([('a', 1), ('b', 2), ('c', 3)])
        'a: 1\nb: 2\nc: 3'
        """
        print lst
        return '\n'.join([field + ': ' + str(value) for (field, value) in lst])
        


def test():
    tup_data = [('a', 1), ('b', 2), ('c', 3)]
    
    qr = QRImg(tup_data, '/tmp/12345.jpg')
    qr.make_image()


if __name__ == "__main__":
    test()

        

    

      