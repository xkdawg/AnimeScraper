import string
import wget
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

queue = [] # queue is a queue data structure that stores the names of recently downloaded anime.

# populateQueue(file) restores the queue to whatever was in the download file from the last run.
# Requires: file is a valid downloaded.txt generated from this program
def populateQueue(file):
	global queue
	lines = file.readlines()
	length = len(queue)
	for i in lines:
		i = i.split('\n', 1)[0]
		if(i in queue):
			continue
		queue.append(i)
	print queue

# updateFile() stores the contents of the queue into downloaded.txt
# effects: edits a file
def updateFile():
	file = open("downloaded.txt", "w+")
	for i in queue:
		file.write(i)
		file.write("\n")
	file.close()

# formatName(text) formats the scraped HTML to create a readable name.
# Requires: text is HTML created from this program
def formatName(text):
	text = text.split('<i>', 1)[-1]
	text = text.split('</i>', 1)[0]
	return text

# formatLink(text) formats the scraped HTML to create a usable link
# Requires: text is HTML created from this program
def formatLink(text):
	text = text.split('href="', 1)[-1]
	text = text.split('" title="', 1)[0]
	text = string.replace(text, "&amp;", "&", 1)
	return text

# downloadFiles(anime) downloads the .torrent files for new anime.
# Requires: anime is a list where the nth item is an anime name, and the (n+1)th item 
#           is the corresponding link.
# Effects: * connects to the internet
#          * downloads files
def downloadFiles(anime):
	length = len(anime)/2
	print(length)

	qlen = len(queue)
	count = 0
	for i in range(length):
		if(qlen==40):
			queue.pop(0)
			qlen-=1
		queue.append(anime[count])
		qlen+=1
		print(anime[count+1] + "\n\n\n")
		wget.download(anime[count+1])
		count+=2
	updateFile()

# getAnime(headlessMode) scrapes HorribleSubs.info for any undownloaded anime, and returns a list
#      of the anime that needs to be downloaded. If headlessMode is disabled, selenium will control
#      a chrome browser to do this.
# Requires : * headlessMode is a boolean 
# Effects  : * Connnects to the internet
def getAnime(headlessMode):
	global queue
	if (headlessMode):
		driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
	else:
		driver = webdriver.Chrome()

	driver.get("http://horriblesubs.info/")
	WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "release-info"))) # waits till the element with the specific id appears
	print "Page Loaded!\n"

	parser = BeautifulSoup(driver.page_source,"html.parser")

	links = parser.findAll("span", {"class" : "dl-link"})
	names = parser.findAll("td", {"class" : "dl-label"})

	download = []
	length = len(links)
	count = 0

	for i in range(length): 
		if(not("www.nyaa.se" in str(links[i]))):
			continue
		if("480p" in str(names[count]) or formatName(str(names[count])) in queue):
			count+=1
			continue
		download.append(formatName(str(names[count])))
		download.append(formatLink(str(links[i])))
		count+=1

	driver.close()
	return download

def main():
	try:
		alreadyDownloaded = open("downloaded.txt", "r+")
	except Exception:
		alreadyDownloaded = open("downloaded.txt", "w+")
	populateQueue(alreadyDownloaded)
	toDownload = getAnime(False)
	downloadFiles(toDownload)


if __name__ == '__main__':
	main()
