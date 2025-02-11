blur_available = True
try:
    from PIL import Image, ImageFilter
except:
    blur_available = False

if blur_available and get("background-blur", False, "gtkwindow"):
    mode = "RGB"

    def pixbuf2image(pix):
        """Convert gdkpixbuf to PIL image"""
        global mode
        data = pix.get_pixels()
        w = pix.props.width
        h = pix.props.height
        stride = pix.props.rowstride
        mode = "RGB"
        if pix.props.has_alpha:
            mode = "RGBA"
        im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
        return im

    def image2pixbuf(im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              (mode == "RGBA"), 8, w, h, w * len(mode))
        return pix

    def blur_draw(px):
        if px:
            im = pixbuf2image(px)
            im = im.filter(ImageFilter.GaussianBlur(
                int(get("background-blur-level", "15", "gtkwindow"))))
            px = image2pixbuf(im)
        return px

    def module_init():
        loginwindow.background_handler = blur_draw
        loginwindow.update_user_background()
else:
    def module_init():
        return
