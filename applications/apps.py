import ui
import re
from html.parser import HTMLParser
import os
import pickle
from oslib import Buffer, BufferUpdate

def load_settings(filename):
    filepath = os.path.join('config', filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return None
def save_settings(filename, data):
    filepath = os.path.join('config', filename)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_p_tag = False
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p' or tag == 'div':
            self.in_p_tag = True

    def handle_data(self, data):
        if self.in_p_tag:
            self.paragraphs.append(data)

    def handle_endtag(self, tag):
        if tag == 'p':
            self.in_p_tag = False

class Bookmark:
    def __init__(self, document, page):
        self.document = document
        self.page = page

class BookSettings:
    def __init__(self):
        self.bookmarks = []
        self.lastPage = Bookmark(0, 0)

class Book:
    def __init__(self, name, epub):
        self.name = name
        self.epub = epub

from oslib import Application, Command, nop

def drawTools(buf, inputs, app, osData):
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height, fill=255)
    if osData["flags"]["keyboard"]:
        text = "".join(osData["keyboardQueue"])
        text_size = ui.text_bounds(text)
        app.variables["cursor"][0] += text_size[0]
        if(app.variables["cursor"][0] >= buf.width):
            app.variables["cursor"][1] += 10
            app.variables["cursor"][0] = 0
        ui.draw_text(buf, app.variables["cursor"][0], app.variables["cursor"][1], text, fill=0)
        osData["flags"]['keyboard'] = False
    return True

def drawHome(buf, inputs, app, osData):
    if inputs[0] == 1:
        app.variables["menu"].select_previous()
    if inputs[2] == 1:
        app.variables["menu"].select_next()
    if inputs[1] == 1:
        global application
        application = app.variables["menu"].options[app.variables["menu"].selection].lower()
        return Command("launch", application)
    else:
        app.variables["menu"].draw(buf, 0, 0, buf.width, buf.height)
    return True

def killReader(app):
    app.variables["readerState"] = "browse"
    app.variables["book"] = None
    app.variables["content"] = None
    app.variables["page"] = 0

def drawStats(buf, book, document, page):
    ui.draw_rectangle(buf, 0, 0, buf.width, 13, fill=255)
    ui.draw_text(buf, 0, 1, book.title[:11]+"...", fill=0)
    ui.draw_text(buf, 89, 1, f"Doc {document}", fill=0)
    ui.draw_text(buf, 131, 1, f"Pg. {page}", fill=0)
    ui.draw_line(buf, 0, 10, buf.width, 10)

def handleReader(buf, inputs, app, osData):
    if(app.variables["readerState"] == "browse"):
        if inputs[0] == 1:
            app.variables["menu"].select_previous()
        if inputs[2] == 1:
            app.variables["menu"].select_next()
        if inputs[1] == 1:
            app.variables["book"] = books[app.variables["menu"].selection].epub
            book = app.variables["book"]
            contents = app.variables["book"].get_item_with_href('Text/Table of Contents.xhtml')
            if(contents):
                app.variables["readerState"] = "contents"
                inputs = [0, 0, 0, 0]
                contents_str = str(contents.get_content())
                links = re.findall(r'<a href="(.*?)">', contents_str)
                links.pop(0)
                app.variables["contentsMenu"] = ui.Menu(links)
            else:
                items = list(book.get_items_of_type(app.variables["ITEM_DOCUMENT"]))
                app.variables["content"] = ui.fix_unicode(str(items[1].get_content()))
                bookSettings = load_settings(app.variables["book"].title + ".pickle")
                if bookSettings is not None:
                    bookmark = bookSettings.bookmarks[-1]
                    app.variables["document"] = bookmark.document
                    app.variables["page"] = bookmark.page
                app.variables["readerState"] = "read"
        else:
            app.variables["menu"].draw(buf, 0, 0, buf.width, buf.height, size=1)
    if(app.variables["readerState"] == "contents"):
        if inputs[0] == 1:
            app.variables["contentsMenu"].select_previous()
        if inputs[2] == 1:
            app.variables["contentsMenu"].select_next()
        if inputs[1] == 1:
            app.variables["content"] = ui.fix_unicode((app.variables["contentsMenu"].options[app.variables["contentsMenu"].selection])[3:].split("#")[0])
            app.variables["readerState"] = "read"
        app.variables["contentsMenu"].draw(buf, 0, 0, buf.width, buf.height, size=1)
    if app.variables["readerState"] == "read":
        if inputs[0] == 1 and app.variables["page"] > 0:
            app.variables["page"] -= 1
            if(app.variables["page"] == 0):
                app.variables["page"] = 1
                app.variables["document"] -= 1
                app.variables["content"] = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[app.variables["document"]].get_content())

        content = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[app.variables["document"]].get_content())
        parser = MyHTMLParser()
        parser.feed(content)
        paragraphs = ui.fix_unicode("\n".join(parser.paragraphs))

        if(app.variables["cachedLines"] == []):
            app.variables["pageTotal"], app.variables["cachedLines"] = ui.draw_page(buf, paragraphs, 1, 0, 0, noRender=True, returnLines=True)
        else:
            app.variables["pageTotal"] = ui.draw_page(buf, paragraphs, 1, 0, 0, noRender=True, cachedLines=app.variables["cachedLines"])

        if inputs[2] == 1:
            app.variables["page"] += 1
            if(app.variables["page"] > app.variables["pageTotal"]):
                app.variables["page"] = 1
                app.variables["document"] += 1
                app.variables["content"] = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[app.variables["document"]].get_content())
                app.variables["cachedLines"] = []

        drawStats(buf, app.variables["book"], app.variables["document"], app.variables["page"])
        app.variables["pageTotal"] = ui.draw_page(buf, paragraphs, 1, 0, app.variables["page"], yoffset=13, cachedLines=app.variables["cachedLines"])

    return True

def createBookmark(app):
    bookSettings = load_settings(app.variables["book"].title + ".pickle")
    if bookSettings is None:
        bookSettings = BookSettings()
    bookSettings.bookmarks.append(Bookmark(app.variables["document"], app.variables["page"]))
    save_settings(app.variables["book"].title + ".pickle", bookSettings)

def loadBookmark(app):
    bookSettings = load_settings(app.variables["book"].title + ".pickle")
    if bookSettings is None:
        return
    bookmark = bookSettings.bookmarks[-1]
    app.variables["document"] = bookmark.document
    app.variables["page"] = bookmark.page
    app.variables["content"] = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[bookmark.document].get_content())

def startDocument(app):
    app.variables["document"] = 0
    app.variables["page"] = 1
    app.variables["content"] = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[0].get_content())

def nextDocument(app):
    app.variables["document"] += 1
    app.variables["page"] = 1
    app.variables["content"] = str(list(app.variables["book"].get_items_of_type(app.variables["ITEM_DOCUMENT"]))[app.variables["document"]].get_content())

books = []
def readerInit(buf, app, osData):
    global books
    from ebooklib import epub, ITEM_DOCUMENT
    books = [ 
    Book("North Woods", epub.read_epub("northwoods.epub")),
    Book("A Brief History Of Time", epub.read_epub("bhot.epub")),
    Book("Project Management", epub.read_epub("pm.epub")),
    Book("365 Days with Self-Discipline", epub.read_epub("selfhelp.epub")),
    ]
    app.variables["menu"] = ui.Menu([book.name for book in books])
    app.variables["ITEM_DOCUMENT"] = ITEM_DOCUMENT
    return True

def homeInit(buf: Buffer, app, osData):
    return True

launcher = Application("launcher", nop, drawHome, nop, {"menu": ui.Menu(["DrawTest", "Reader", "Tools"])})
reader = Application("reader", readerInit, handleReader, killReader, {"readerState": "browse", "book": None, "content": None, "page": 1, "pageTotal": 1, "document": 0, "cachedLines": []}, {"Next Document": nextDocument, "To Start": startDocument, "Create Bookmark": createBookmark, "Load Bookmark": loadBookmark})
tools = Application("tools", nop, drawTools, nop, {"cursor": [0, 0]})
