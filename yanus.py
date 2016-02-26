import os
import time
import urllib.request as req
from urllib.error import URLError, HTTPError

class Yanus:
    def __init__(self, start_url, sandbox):
        self.start_url = start_url
        self.sandbox = sandbox
        self.url_queue = []
        self.processed_urls = []
        self.bytes_downloaded = 0
        self.urls_visited = 0
        self.urls_error = 0
        self.pics_downloaded = 0
        self.exe_downloaded = 0
        self.music_downloaded = 0
        self.movies_downloaded = 0

    def run(self):
        self.init_url_queue()
        self.init_folders()
        cycles = 500
        while 1:
            res = self.process_url()
            if not res:
                break
            cycles -= 1
            if cycles == 0:
                break

    def init_url_queue(self):
        self.url_queue = []
        self.url_queue.append(self.start_url)
        self.processed_urls = []

    def init_folders(self):
        self.pics_folder = self.sandbox + "pictures\\"
        if not os.path.exists(self.pics_folder): os.makedirs(self.pics_folder)
        pass
        self.movies_folder = self.sandbox + "movies\\"
        if not os.path.exists(self.movies_folder): os.makedirs(self.movies_folder)
        pass
        self.exe_folder = self.sandbox + "exe\\"
        if not os.path.exists(self.exe_folder): os.makedirs(self.exe_folder)
        pass
        self.music_folder = self.sandbox + "music\\"
        if not os.path.exists(self.music_folder): os.makedirs(self.music_folder)

    def process_url(self):
        if len(self.url_queue) == 0:
            print("All URLs processed, exiting...")
            return False
        url = self.url_queue[0]
        self.url_queue = self.url_queue[1:]
        print("Processing URL: " + url)
        self.processed_urls.append(url)
        if url[-1:] == "/": url = url[:-1]  # strip trailing slash
        if url[-4:] == ".exe":
            self.download_bin(url, self.exe_folder)
            self.exe_downloaded += 1
        elif url[-4:] in [".jpg", ".bmp", ".png", ".gif"]:
            self.download_bin(url, self.pics_folder)
            self.pics_downloaded += 1
        elif url[-4:] in [".avi", ".mkv", ".wmv", ".mp4"]:
            self.download_bin(url, self.movies_folder)
            self.movies_downloaded += 1
        elif url[-4:] in [".mp3", ".wav"]:
            self.download_bin(url, self.music_folder)
            self.music_downloaded += 1
        else:
            html = self.download_html(url)
            urls = self.parse_html(html)
            self.update_url_list(urls)
        return True

    def get_file_name(self, url):
        i = url.rfind("/")
        if i == -1:
            return str(int(round(time.time() * 1000))) + url[-4:]
        return url[i+1:]

    def download_bin(self, url, folder):
        filename = folder + self.get_file_name(url)
        try:
            (fname, headers) = req.urlretrieve(url, filename)
        except HTTPError as e:
            print("... cannot process URL (" + str(e.code) + ") '" + url + "'")
            self.urls_error += 1
        except URLError as e:
            print("... cannot process URL (" + str(e.reason) + ") '" + url + "'")
            self.urls_error += 1
        except Exception as e:
            print("... cannot process URL (" + "other error" + ") '" + url + "'")
            self.urls_error += 1
        else:
            print("downloaded file " + filename)
            #self.bytes_downloaded += len(b)
            self.urls_visited += 1

    def download_html(self, url):
        s = ""
        try:
            resp = req.urlopen(url)
        except HTTPError as e:
            print("... cannot process URL (" + str(e.code) + ") '" + url + "'")
            self.urls_error += 1
        except URLError as e:
            print("... cannot process URL (" + str(e.reason) + ") '" + url + "'")
            self.urls_error += 1
        except Exception as e:
            print("... cannot process URL (" + "other error"  + ") '" + url + "'")
            self.urls_error += 1
        else:
            try:
                s = resp.read().decode("utf-8", "ignore")
            except Exception as e:
                print("... cannot process URL (" + "decoding error"  + ") '" + url + "'")
                self.urls_error += 1
            else:
                print("downloaded " + str(len(s)) + " symbols")
                self.bytes_downloaded += len(s)
                self.urls_visited += 1
        return s

    def sample_html(self, url):
        return """
        <body>
            <a href="http://www.mail.ru" >
        test test test
            <a href="http://www.google.com" >
                    test test test
            <a href="http://www.microsoft.com" >
        </body>
        """

    def parse_html(self, html: str):
        s = html[:].lower()
        urls = []
        while 1:
            i = s.find("<a")
            if i == -1: break
            s = s[i:]
            k = s.find("href=")
            if k == -1: break
            k += 6
            url = ""
            while 1:
                if k >= len(s): break
                if s[k] == '"':
                    k += 1
                    break
                url += s[k]
                k += 1
            if len(url) > 7 and url[0:4] == "http":
                urls.append(url)
            else:
                pass #print("...wrong URL: " + url)
            s = s[k:]
        return urls

    def update_url_list(self, urls):
        new_url_queue = self.url_queue[:]
        for url in urls:
            if url not in new_url_queue and url not in self.processed_urls:
                new_url_queue.append(url)
                #print("...added new url to queue: " + url)
            else:
                pass #print("...skipped duplicated url: " + url)
        self.url_queue = new_url_queue[:]



if __name__ == "__main__":
    yanus = Yanus(r"http://money.cnn.com", "c:\\temp\\")
    millis_start = int(round(time.time() * 1000))
    yanus.run()
    millis_end = int(round(time.time() * 1000))
    print("\n\nFinal list of processed URLs:")
    for url in yanus.processed_urls:
        print(url)
    milliseconds = millis_end - millis_start
    seconds = milliseconds//1000
    minutes = seconds//60
    hours = minutes//60
    s = "<h2>Statistics:</h2><br>"
    s += "processing time: " + str(hours) + " hours, " + str(minutes) + " minutes, " + str(seconds) + " seconds<br>"
    s += "URLs visited: " + str(yanus.urls_visited) + "<br>"
    s += "URLs failed: " + str(yanus.urls_error) + "<br>"
    s += "Bytes downloaded " + str(yanus.bytes_downloaded) + "<br>"
    s += "Pictures downloaded " + str(yanus.pics_downloaded) + "<br>"
    s += "Exe downloaded " + str(yanus.exe_downloaded) + "<br>"
    s += "Music files downloaded " + str(yanus.music_downloaded) + "<br>"
    s += "Movies downloaded " + str(yanus.movies_downloaded) + "<br>"
    print(s)  # I used my smtp client to send e-mail with this report
