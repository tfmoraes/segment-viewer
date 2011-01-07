import sys

import Image
import numpy as np
import wx

from scipy.misc import imshow
from scipy.ndimage import watershed_ift

class ImageViewer(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self._build_gui()
        self._binds()
        self.Show()

        self.mask = None

    def _build_gui(self):
        self.viewer = wx.StaticBitmap(self, -1)
        self.btn_segment = wx.Button(self, -1, 'Segment')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.viewer, 0, wx.EXPAND)
        sizer.Add(self.btn_segment, 0, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()
        self.Update()
        self.SetAutoLayout(1)

    def _binds(self):
        self.viewer.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.viewer.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.btn_segment.Bind(wx.EVT_BUTTON, self.on_segment)

    def on_left_click(self, evt):
        x, y = evt.GetX(), evt.GetY()
        v = 1
        c = (0, 0, 255)
        self._do_markers(x, y, v, c)
        blend = self._do_blend(self.img, self.mask)
        self._paint_image(blend)

    def on_right_click(self, evt):
        x, y = evt.GetX(), evt.GetY()
        v = -1
        c = (255, 0, 0)
        self._do_markers(x, y, v, c)
        blend = self._do_blend(self.img, self.mask)
        self._paint_image(blend)

    def on_segment(self, evt):
        o = np.zeros_like(self._markers)
        watershed_ift(self.img[:,:, 0], self._markers, output=o)
        o = o * 255
        imshow(o.astype('uint8'))


    def _do_markers(self, x, y, v, c):
        if self.mask is None:
            self.mask = np.zeros_like(self.img)
            self._markers = np.zeros(self.img.shape[:2], 'int')

        self._markers[y, x] = v
        self.mask[y, x]  = [255, 0, 0]

    def _do_blend(self, img, mask):
        ca = 0.3
        cb = 0.9
        return (mask*ca + img*cb*(1-ca)).astype('uint8')

    def _paint_image(self, img):
        height, width = img.shape[:2]
        image = wx.EmptyImage(width, height)
        image.SetData(img.tostring())
        bmp = image.ConvertToBitmap()
        self.viewer.SetBitmap(bmp)
        self.Layout()

    def set_image(self, img):
        self.img = img
        self._paint_image(img)

def load_image(filename):
    img = Image.open(filename)
    img.convert(mode='RGB')
    return np.asarray(img)

if __name__ == '__main__':
    img = load_image(sys.argv[-1])

    app = wx.App()

    image_viewer = ImageViewer(None, 'Image viewer')
    image_viewer.set_image(img)
    app.SetTopWindow(image_viewer)
    app.MainLoop()

