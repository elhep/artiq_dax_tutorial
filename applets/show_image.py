#!/usr/bin/env python3

import PyQt5  # make sure pyqtgraph imports Qt5
import pyqtgraph

from artiq.applets.simple import SimpleApplet


class Image(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.view = self.addViewBox()
        self.img_item = pyqtgraph.ImageItem()
        self.view.addItem(self.img_item)
        self.view.setAspectLocked(True)

    def data_changed(self, data, mods):
        try:
            img = data[self.args.img][1]
        except KeyError:
            return
        self.img_item.setImage(img)


def main():
    applet = SimpleApplet(Image)
    applet.add_dataset("img", "image data (2D numpy array)")
    applet.run()

if __name__ == "__main__":
    main()
