import ui
import re
from ebooklib import epub, ITEM_DOCUMENT
from html.parser import HTMLParser
import os
import pickle

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
        
books = [ 
    Book("Project Management", epub.read_epub("pm.epub")),
    Book("Lovecraft", epub.read_epub("lovecraft.epub")), 
    Book("A Brief History Of Time", epub.read_epub("bhot.epub")),
    Book("365 Days with Self-Discipline", epub.read_epub("selfhelp.epub")),
]

class Application:
    def __init__(self, name, init, run, kill, variables, menuOptions={}):
        self.name = name
        self.init = init
        self.run = run
        self.kill = kill
        self.variables = variables
        self.menuOptions = menuOptions

def nop(*args):
    pass

def drawTools(buf, inputs, app):
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height, fill=0)
    if inputs[0] == 1:
        ui.draw_text(buf, 10, 10, "Sorry, nothing yet", fill=255)
    return True

def drawHome(buf, inputs, app):
    if inputs[0] == 1:
        app.variables["menu"].select_previous()
    if inputs[2] == 1:
        app.variables["menu"].select_next()
    if inputs[1] == 1:
        global application
        application = app.variables["menu"].options[app.variables["menu"].selection].lower()
        return application
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
    ui.draw_text(buf, 0, 1, book.title[:10]+"...", fill=0)
    ui.draw_text(buf, 85, 1, f"Chap {document}", fill=0)
    ui.draw_text(buf, 130, 1, f"Page {page}", fill=0)
    ui.draw_line(buf, 0, 10, buf.width, 10)

def handleReader(buf, inputs, app):
    if(app.variables["readerState"] == "browse"):
        if inputs[0] == 1:
            print(app.variables["menu"].select_previous())
        if inputs[2] == 1:
            print(app.variables["menu"].select_next())
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
                items = list(book.get_items_of_type(ITEM_DOCUMENT))
                print(items[1].get_content())
                app.variables["content"] = ui.fix_unicode(str(items[1].get_content()))
                app.variables["readerState"] = "read"
        else:
            app.variables["menu"].draw(buf, 0, 0, buf.width, buf.height)
    if(app.variables["readerState"] == "contents"):
        if inputs[0] == 1:
            print(app.variables["contentsMenu"].select_previous())
        if inputs[2] == 1:
            print(app.variables["contentsMenu"].select_next())
        if inputs[1] == 1:
            app.variables["content"] = ui.fix_unicode((app.variables["contentsMenu"].options[app.variables["contentsMenu"].selection])[3:].split("#")[0])
            app.variables["readerState"] = "read"
        app.variables["contentsMenu"].draw(buf, 0, 0, buf.width, buf.height)
    if app.variables["readerState"] == "read":
        document = app.variables["document"]
        page = app.variables["page"]
        if inputs[0] == 1 and page > 0:
            app.variables["page"] -= 1

        content = str(list(app.variables["book"].get_items_of_type(ITEM_DOCUMENT))[document].get_content())
        parser = MyHTMLParser()
        parser.feed(content)
        paragraphs = ui.fix_unicode("\n".join(parser.paragraphs))

        app.variables["pageTotal"] = ui.draw_page(buf, paragraphs, 1, 0, 0, noRender=True)

        if inputs[2] == 1:
            print(f"{document} {page} {app.variables['pageTotal']}")
            if page < app.variables["pageTotal"]:
                app.variables["page"] += 1
            else:
                app.variables["page"] = 1
                app.variables["document"] += 1
                app.variables["content"] = str(list(app.variables["book"].get_items_of_type(ITEM_DOCUMENT))[document].get_content())

        drawStats(buf, app.variables["book"], document, page)
        app.variables["pageTotal"] = ui.draw_page(buf, paragraphs, 1, 0, app.variables["page"] - 1, yoffset=13)

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
    app.variables["content"] = str(list(app.variables["book"].get_items_of_type(ITEM_DOCUMENT))[bookmark.document].get_content())

def nextDocument(app):
    app.variables["document"] += 1
    app.variables["page"] = 1
    app.variables["content"] = str(list(app.variables["book"].get_items_of_type(ITEM_DOCUMENT))[app.variables["document"]].get_content())

launcher = Application("launcher", nop, drawHome, nop, {"menu": ui.Menu(["Reader", "Tools"])})
reader = Application("reader", nop, handleReader, killReader, {"menu": ui.Menu([book.name for book in books]), "readerState": "browse", "book": None, "content": None, "page": 1, "pageTotal": 1, "document": 0}, {"Next Document": nextDocument, "Create Bookmark": createBookmark, "Load Bookmark": loadBookmark})
tools = Application("tools", nop, drawTools, nop, {})
