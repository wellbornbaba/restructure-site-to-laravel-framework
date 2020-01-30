import os,sys, requests
from re import findall, sub
from shutil import copy2, copytree
from urllib.parse import urlparse, urljoin
import queue
import logging
import tkinter as tk
from tkinter import N, S, E, W
from urllib.parse import urlparse
import sqlite3
from bs4 import BeautifulSoup as bs
import tldextract
from glob import iglob
#learn more simple beautiful here https://kite.com/python/examples/1724/BeautifulSoup-filter-tags-with-a-list-of-criteria

class Db:
    def __init__(self, dbname):
        try:
            self.con = sqlite3.connect(dbname, check_same_thread=False)
            self.con.row_factory = sqlite3.Row
            self.cur = self.con.cursor()
        except Exception as e:
            print("Error connecting to db: "+ str(e))

    def createtable(self, table, param):
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({param})")
        self.con.commit()

    def fetch(self, param):
        self.cur.execute(param)
        return self.cur.fetchall()

    def insert(self, table, paramname, paramvalue):
        self.cur.execute(
            f"INSERT INTO {table} ({paramname}) VALUES({paramvalue})")
        self.con.commit()

    def check(self, checkval, table, param):
        self.cur.execute(f"SELECT {checkval} FROM {table} WHERE {param}")
        return self.cur.fetchone()

    def others(self, param):
        self.cur.execute(param)
        self.con.commit()

    def getTotal(self, param):
        totalrow = self.cur.execute(param).rowcount
        return totalrow

    def __del__(self):
        self.con.close()


# text bindings
'''
self._text.bind('<Configure>', self.on_configure)
self._text.bind('<FocusOut>', self.on_focus_out)
self._text.bind('<KeyPress-Escape>', self.on_escape_press)
self._text.bind('<KeyPress-BackSpace>', self.on_backspace_press)
self._text.bind('<KeyPress>', self.on_key_press)
self._text.bind('<Any-Button>', self.on_button)
self._text.bind('<Motion>', lambda e: 'break')
<Button-1>

    A mouse button is pressed over the widget. Button 1 is the leftmost button, button 2 is the middle button (where available), and button 3 the rightmost button. When you press down a mouse button over a widget, Tkinter will automatically “grab” the mouse pointer, and subsequent mouse events (e.g. Motion and Release events) will then be sent to the current widget as long as the mouse button is held down, even if the mouse is moved outside the current widget. The current position of the mouse pointer (relative to the widget) is provided in the x and y members of the event object passed to the callback.

    You can use ButtonPress instead of Button, or even leave it out completely: <Button-1>, <ButtonPress-1>, and <1> are all synonyms. For clarity, I prefer the <Button-1> syntax.
<B1-Motion>

    The mouse is moved, with mouse button 1 being held down (use B2 for the middle button, B3 for the right button). The current position of the mouse pointer is provided in the x and y members of the event object passed to the callback.
<ButtonRelease-1>

    Button 1 was released. The current position of the mouse pointer is provided in the x and y members of the event object passed to the callback.
<Double-Button-1>

    Button 1 was double clicked. You can use Double or Triple as prefixes. Note that if you bind to both a single click (<Button-1>) and a double click, both bindings will be called.
<Enter>

    The mouse pointer entered the widget (this event doesn’t mean that the user pressed the Enter key!).
<Leave>

    The mouse pointer left the widget.
<FocusIn>

    Keyboard focus was moved to this widget, or to a child of this widget.
<FocusOut>

    Keyboard focus was moved from this widget to another widget.
<Return>

    The user pressed the Enter key. You can bind to virtually all keys on the keyboard. For an ordinary 102-key PC-style keyboard, the special keys are Cancel (the Break key), BackSpace, Tab, Return(the Enter key), Shift_L (any Shift key), Control_L (any Control key), Alt_L (any Alt key), Pause, Caps_Lock, Escape, Prior (Page Up), Next (Page Down), End, Home, Left, Up, Right, Down, Print, Insert, Delete, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, Num_Lock, and Scroll_Lock.
<Key>

    The user pressed any key. The key is provided in the char member of the event object passed to the callback (this is an empty string for special keys).
a

    The user typed an “a”. Most printable characters can be used as is. The exceptions are space (<space>) and less than (<less>). Note that 1 is a keyboard binding, while <1> is a button binding.
<Shift-Up>

    The user pressed the Up arrow, while holding the Shift key pressed. You can use prefixes like Alt, Shift, and Control.
<Configure>

    The widget changed size (or location, on some platforms). The new size is provided in the width and height attributes of the event object passed to the callback.

'''
logger = logging.getLogger(__name__)

# https://www.tutorialspoint.com/python/tk_text.htm
def foldersize(path):
    '''
    Get total folder size
    '''
    total = 0
    if os.path.exists(path):
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += foldersize(entry.path)
            return total
        except Exception:
            return total


def domainname(url):
    '''
    Get domain name only from url e.g google.com
    '''
    domain = urldomains(url)
    r = os.path.splitext(getdomain_only(domain))[0].split('.')[-1]
    return r


def convertbyte(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    step_unit = 1000.0 #1024 bad the size

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit


def cleanString(words):
    '''
    Remove all bad characters to only accept this characters A-Za-z0-9-._
    '''
    r = sub('[^A-Za-z0-9-._ ]+', '', words)
    return r.replace('_', ' ').replace('-', ' ')


def cleantitle(words):
    '''
    Remove all bad characters to only accept this characters A-Za-z0-9-._
    '''
    r = sub('[^A-Za-z0-9-._]+', '', words)
    return r.replace('_', '-')


def hidebutton(widget):
    widget.place(x=150, y=100)
    widget.place_forget()


def showbutton(widget):
    widget.grid()


def wordExit(data, words):
    '''
    data: the string data to search from
    words: the word to find in data
    '''
    if words in data:
        return True
    else:
        return ''


def is_url(url):
    '''
    Check if this is a url
    '''
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def isurl(url):
    if 'http' in url or 'https' in url or '//' in url:
        return True
    else:
        return False


class QueueProcess(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleTk:
    """Get All messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame, widget, inseconds=100):
        self.insec = inseconds
        self.frame = frame
        self.scrolled_text = widget
        # Create a ScrolledText wdiget
        #self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        #self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        # self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config(
            'CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueProcess(self.log_queue)
        #formatter = logging.Formatter('%(asctime)s: %(message)s')
        formatter = logging.Formatter('%(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(self.insec, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(self.insec, self.poll_log_queue)


def logconsole(level, msg):
    lvl = getattr(logging, level.upper())
    logger.log(lvl, msg)


def remove_duplicatelist(x):
    return list(dict.fromkeys(x))


def normalpath(path):
    return os.path.normpath(path).replace("\\", "/")


def joinpath(part1, part2):
    return normalpath(os.path.join(part1, part2))


def remove_firstpath_dir(dirs):
    t = normalpath(dirs)
    c = t.split("/").pop(0)
    d = t.replace(c + '/', '')
    return d


def log(key, logpath, name):
    thepath = joinpath(logpath, name)
    key_file = open(thepath, "a", encoding='utf-8')
    key_file.write(str(key))
    key_file.close()


def urlfolder(url):
    isparsed = urlparse(url).path.lstrip('/')
    return normalpath(os.path.dirname(isparsed)).replace('.','')


def getfolder(url, domain):
    folder = url.replace('../', '')
    folder = urlfolder(folder)
    domain = domaintld(domain, 'tld')
    return joinpath(domain, folder)+'/'


def urldomain(url):
    return urljoin(url, '/')


def urldomains(url):
    return urljoin(url, '/').rstrip('/')


def getdomain_only(url):
    return urldomains(url).split(':')[1].replace('/', '')


def new_urlpath(url):
    a_href_path = urlfolder(url)
    # a_href_ext = os.path.splitext(a_href)[1]
    # we get the basename of the actual linked url
    a_href_basename = os.path.basename(url)
    # here we get new created url path
    a_href_new_path = joinpath(a_href_path, a_href_basename)
    return a_href_new_path


def firstpath_name(url, index=0):
    '''Use to get directory from url link\n
       URL: fullpath e.g: http://www.mysite.com/file/file2/file3/file.html\n
       INDEX: pass the int number of directory you want e.g: 0 get file, 1 get file2\n
       INDEX: is optional\n
    '''
    hold = urlfolder(url)
    result = hold.split("/")
    total = len(result)
    if not index:
        return result.pop(0)
    elif total > index:
        return result.pop(total - index)
    elif total < index:
        return result.pop(index - total)
    else:
        return result.pop(0)


def copydir(from_file, to_file):
    try:
        if os.path.exists(from_file):
            copytree(from_file, to_file)
            #result = 'Folder copied: ' + from_file + ' TO ' + to_file
        else:
            #result = "Can't Folder file: " + from_file + ' TO ' + to_file
            pass
    except Exception as e:
        result = 'Copying folder function error: ' + str(e)
        print('-> ' + result)


def copyfiles(from_file, to_file):
    try:
        if os.path.exists(from_file):
            copy2(from_file, to_file)
            #result = 'File copied: ' + from_file + ' TO ' + to_file
        else:
            #result = "Can't copy file: " + from_file + ' TO ' + to_file
            pass

    except Exception as e:
        result = 'Copying function error: ' + str(e)
        print('-> ' + result)


def makefolder(dirpath):
    if not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath)
        except Exception:
            pass


def firstfolder(dirpath):
    return normalpath(os.path.dirname(dirpath))


def parse_css_js(filed, path, extra=''):
    '''
    Find and replace url links in CSS, SCSS OR JS files
    File: is the file full url e.g style.css or style.js
    Path: is the path to repalce with e.g images
    Extra is optional like passing full url or symbol to get fullpath e.g {{url}} or http://yoursite.com/
    '''
    tylist = ['.ttf', '.woff', '.woff2', '.eot', '.less', '.otf', '.docx', '.svg', '.ac']

    if os.path.isfile(filed) and os.path.exists(filed):
        html_content = localread_file(filed)
    else:
        html_content = filed

    try:
        soupbackground_image = findall(r'url\((.*?)\)', html_content)
        for cssjsurl in soupbackground_image:
            oldurl = cssjsurl.replace('"', '').replace("'", '').replace('..', '')
            oldbase = basename(oldurl)
            ext = os.path.splitext(cssjsurl)[1]
            if '?' in ext:
                # this handles cases of file.eot?#somethin
                # so get a clean extension
                ext = ext.split('?')[0]

            if '#' in ext:
                # this handles cases of file.eot?#somethin
                # so get a clean extension
                ext = ext.split('#')[0]

            if ext in tylist:
                dfolder = '../fonts'
            else:
                dfolder = '../images'

            newurlpath = joinpath(dfolder, oldbase)
            html_content = html_content.replace(cssjsurl, newurlpath)

        return html_content
    except Exception as e:
        return 'Error occured: ' + str(e)


def internet_on():
    try:
        response = requests.get('http://ip.42.pl/raw', headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            return 'on'
    except Exception:
        return 'off'


def localread_file(dfile):
    try:
        with open(dfile, 'r', encoding='utf-8') as fp:
            text = fp.read()
            fp.close()  # clean up
            return text

    except Exception:
        return False


def localwrite_file(dfile, txt):
    try:
        with open(dfile, 'w', encoding='utf-8') as fp:
            fp.write(txt.replace('\r\n', '\n'))
            fp.close()  # clean up
            return True

    except Exception:
        return False


def remoteread_file(dfile, proxy=''):
    try:
        with requests.get(dfile, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:70.0) Gecko/20100101 Firefox/70.0'},
                          verify=False, stream=True, proxies={"http": proxy, "https": proxy}) as response:
            allowcode = [200, 202, 201, 203, 206, 302, 301, 303, 305, 307, 404]
            if response.status_code in allowcode:
                # now proceed with the grabbing
                return response.content.decode('utf-8')
            else:
                return response.status_code
    except Exception as e:
        print('Requests '+ str(e))
        return False


def getproxy():
    #https://free-proxy-list.net/
    # check http://httpbin.org/ip
    proxycontent = remoteread_file('https://free-proxy-list.net/')
    proxycontent = bs(proxycontent, 'html.parser')
    proxycontent = proxycontent.find('table', class_='table-striped')
    rows = []
    trs = proxycontent.find_all('tr')
    headerow = [td.get_text(strip=True)
                for td in trs[0].find_all('th')]  # header row
    if headerow:  # if there is a header row include first
        # rows.append(headerow)
        trs = trs[1:]

    for tr in trs:  # for every table row
        tds = tr.find_all('td')
        try:
            ipaddress, port, code, country, anonymity, google, https, lastchecked = [
                td.get_text(strip=True) for td in tds]
            # data row
            if 'yes' in https:
                rows.append(ipaddress + ':' + port)

        except:
            pass

    return rows


def findemail(txt):
    match = findall(r'[\w\.-]+@[\w\.-]+', txt)
    #find type of domain email
    #re.findall(r'[\w-\._\+%]+@test\.com',text)
    return match


def findphone(txt):
    match = findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', txt)
    return match


def remotedownload_file(dfile, tofile, proxy=''):
    #list_table = getproxy()
    #n = random.randint(0, 100)
    #proxy = list_table[n]
    #r = requests.get('http://httpbin.org/ip', headers={'User-Agent': 'Mozilla/5.0'}, proxies={"http": proxy, "https": proxy})
    #print(r.json())
    try:
        with requests.get(dfile, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:70.0) Gecko/20100101 Firefox/70.0'},
                         verify=False, stream=True, proxies={"http": proxy, "https": proxy}) as r:
            allowcode = [200, 202, 201, 203, 206, 302, 301, 303, 305, 307, 404]
            #print(str(r.status_code))
            if r.status_code in allowcode:
                with open(tofile, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                return False


    except Exception:
        return False


def localpaths(url):
    pathlink = ''
    if '/' in url:
        totlen = len(url.split('/'))

        for i in range(totlen):
            pathlink += '../'
            print(i)
    else:
        if url:
            pathlink = '../'

    return pathlink


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return joinpath(base_path, relative_path)


def basename(url):
    '''
    Get the base name of a given url
    base on os.path.basename
    '''
    #clean files pls
    return os.path.basename(url.rstrip('/'))


def exts(url):
    '''
    Get the base name of a given url
    base on os.path.basename
    '''
    #clean files pls
    if '#' in url:
        url = url.split('#')[0]
    if '?' in url:
        url = url.split('?')[0]

    base = basename(url)

    if base:
        hold = os.path.splitext(base.rstrip('/'))[1]
    else:
        hold =''
    return hold


def cleanurl(maindomain, url):
    if not is_url(url):
        maindomain = maindomain.lstrip('/')
        furl = '/' + url.replace('../', '').lstrip('/').lstrip('#').lstrip('?')

        return maindomain + furl

    return url


def downloadremote(fromfile, tofile):
    try:
        r = requests.get(fromfile, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:70.0) Gecko/20100101 Firefox/70.0'}, verify=False, stream=True)
        allowcode = [200, 202, 201, 203, 206, 302, 301, 303, 305, 307, 404]
        if r.status_code in allowcode:
            if not os.path.exists(tofile):
                with open(tofile, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            return True
        else:
            return r.status_code
    except Exception as e:
        return 'Downloading accessing error: ' + str(e)


def browseurl(url):
    try:
        response = requests.get(
            url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:70.0) Gecko/20100101 Firefox/70.0'}, verify=False, stream=True)
        #Request(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        allowcode = [200, 202, 201, 203, 206, 302, 301, 303, 305, 307, 404]
        if response.status_code in allowcode:
            # now proceed with the grabbing
            return response.content
        else:
            return response.status_code
    except Exception as e:
        return 'Url accessing error: ' + str(e)


def isParsable(url):
    parselist  = ['.html', '.htm', '.html5', '.php', '.py', '.java', '.blade', '.aspx', '.css', '.scss']
    base = basename(url)
    checkextension = exts(base)
    if checkextension:
        if checkextension in parselist:
            return True
        else:
            return False
    else:
        return True


def minetype(tp):
    import mimetypes
    r = mimetypes.MimeTypes().guess_type(tp)[0]
    if 'image' in r:
        return 'images'
    elif 'css' in r:
        return 'css'
    elif 'plain' in r:
        return 'text'
    elif '.scss' in tp:
        return 'css'
    elif '.php' in tp:
        return 'html'
    elif 'html' in r:
        return 'html'
    elif 'video' in r:
        return 'video'
    elif 'audio' in r:
        return 'audio'
    elif 'application' in r:
        return 'application'
    else:
        return 'unknow'


def getdomain(url):
    #url
    bb =''
    u = urldomains(url)
    b = u.split('.')
    c = len(b)
    if c == 2 or c == 3:
       bb = '.'.join(b).split('/')[-1]
    elif c > 3:
       bb = '.'.join(u.split('.')[-3:])
    #return str(c) +' -- '+ str(b) +' -- '+ str(bb)
    return str(bb)


def domaintld(url, types=''):
    #https://github.com/john-kurkowski/tldextract
    #ext = tldextract.TLDExtract(suffix_list_url="http://foo.bar.baz")
    try:
        custom_cache_extract = tldextract.TLDExtract(cache_file=resource_path('tld'))
        #ext = tldextract.extract(url)
        ext = custom_cache_extract(url)
        if types == 'name':
            return ext.domain
        elif types == 'tld':
            return ext.suffix
        elif types == 'sub':
            return ext.subdomain
        elif types == 'domain':
            return ext.domain+'.'+ext.suffix
        else:
            return ext.subdomain + '.' + ext.domain + '.' + ext.suffix
    except:
        return getdomain(url)


def domainToParse(sitelink):
    return sitelink.replace('https://www.', '').replace('http://www', '').replace('https://', '').replace('http://', '').rstrip('/')


def findReplace(path, search_extension, replace_extenstion):
    '''
    path: is the folder to search
    search_extension: is the extension to find e.g: .css
    replace_extension: is the extension to replace with e.g: .scss
    '''
    result = ''
    # "*" is for subdirectory
    if os.path.exists(path):
        if not os.path.exists(path + '_bkup'):
            copydir(path, path + '_bkup')

        for foundfile in iglob(joinpath(path,  "**/*" + search_extension), recursive=True):
            if foundfile.endswith(search_extension):
                foundfilename = os.path.splitext(foundfile)[0] + replace_extenstion
                try:
                    os.rename(foundfile, foundfilename)
                    result += foundfile + ' => ' + foundfilename + '\n'

                except Exception:
                    pass
            else:
                pass

        if not result:
            result = 'No  file found [' + search_extension + ']'

        result = replace_extenstion.upper() + ' CONVERTED RESULTS\n=====================================\n' + result
        log(result, path, '_LogResult.txt')
    else:
        print('Path location can not be found.')


def scrapContentUrl(dcontent, url):
    '''
    dcontent:  is the content to parse
    url: must be full url e.g http://google.com
    '''
    url.rstrip('/') #remove ending tralling /
    result = []
    #get all background embeded in style url
    try:
        soupbackground_image = findall(r'url\((.*?)\)', dcontent)
        for cssjsurl in soupbackground_image:
            oldurl = cssjsurl.replace('"', '').replace( "'", '').replace('..', '')

            checkoldbase = oldurl[0]
            if checkoldbase == '/':
                downloadableurl = url + oldurl
            else:
                downloadableurl = url + '/' + oldurl

            result.append(downloadableurl)

    except Exception as e:
        result.append(str(e))
        pass

    #beautiful soup magic start here
    dcontent = bs(dcontent, 'html.parser')

    #get all url a tags
    try:
        for a_stag in dcontent.find_all('a'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["href"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url link tags
    try:
        for a_stag in dcontent.find_all('link'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["href"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url script tags
    try:
        for a_stag in dcontent.find_all('script'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["src"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url img tags
    try:
        for a_stag in dcontent.find_all('img'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["src"]))

    except Exception as e:
        result.append(str(e))
        pass

    #return the whole extracted array
    return result


def scrapFindContentUrl(dcontent, url, divname='', tagname='', tagatt=''):
    '''
    dcontent:  is the content to parse
    url: must be full url e.g http://google.com
    divname: div name or span
    tagname: Tag name must be either class or id
    tagatt: value of the tagname e.g container
    '''

    #beautiful soup magic start here
    dcontent = bs(dcontent, 'html.parser')
    url.rstrip('/') #remove ending tralling /
    result = []

    if divname:
        tagname = tagname.lower()
        htmlclasslist = []
        if ',' in tagatt:
            for ex in tagatt.split(','):
                if ex:
                    htmlclasslist.append(ex.strip())
        else:
            htmlclasslist.append(tagatt.strip())

        if tagname == 'id':
            for foundhtml in dcontent.find_all(divname, id=htmlclasslist):
                dcontent = foundhtml
        else:
            for foundhtml in dcontent.find_all(divname, class_=htmlclasslist):
                dcontent = foundhtml

    #get all background embeded in style url
    try:
        soupbackground_image = findall(r'url\((.*?)\)', dcontent)
        for cssjsurl in soupbackground_image:
            oldurl = cssjsurl.replace('"', '').replace( "'", '').replace('..', '')

            checkoldbase = oldurl[0]
            if checkoldbase == '/':
                downloadableurl = url + oldurl
            else:
                downloadableurl = url + '/' + oldurl

            result.append(downloadableurl)

    except Exception as e:
        result.append(str(e))
        pass

    #beautiful soup magic start here
    #dcontent = bs(dcontent, 'html.parser')

    #get all url a tags
    try:
        for a_stag in dcontent.find_all('a'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["href"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url link tags
    try:
        for a_stag in dcontent.find_all('link'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["href"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url script tags
    try:
        for a_stag in dcontent.find_all('script'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["src"]))

    except Exception as e:
        result.append(str(e))
        pass

    #get all url img tags
    try:
        for a_stag in dcontent.find_all('img'):
            #save for the next parsing must be full url
            result.append(cleanurl(url, a_stag["src"]))

    except Exception as e:
        result.append(str(e))
        pass

    #return the whole extracted array
    return result