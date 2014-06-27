#!/usr/bin/python

import os
import sys
import random
from urlparse import urlparse
from bs4 import BeautifulSoup
from urllib2 import urlopen

#define functions
def gen_soup(url):
	html = urlopen(url).read()
	return BeautifulSoup(html, "lxml")

def get_id(query):
	for var in query.split('&'):
		if (var.startswith("fdid=")):
			return var[5:]
	return str(random.random())[2:]

def parse_project(href):
	url = href['href']
	project_html = gen_soup(url)
	header = project_html.find(id="appheader")
	parsed_url = urlparse(url)
	project = {}
	project["id"] = get_id(parsed_url.query)
	project["title"] = header.p.span.string
	project["description"] = header.p.text
	for a in project_html.findAll("a"):
		if a.text == "download apk":
			project['apk_url'] = a['href']
		if a.text == "source tarball":
			project['source_url'] = a['href']
	return project

def get_projects(url, page, category, numberapps):
	print "Parsing all projects ..."
	projects = []
	stop = False
	while (not stop and len(projects) < numberapps):
		print "Parsing page " + str(page)
		url = URL.format(category,str(page))
		soup = gen_soup(url)
		post_entry = soup.find("div", "post-entry")
		if post_entry.findAll(id="appheader"):
			for project in post_entry.findAll(id="appheader"):
				if (len(projects) >= numberapps):
					break
				projects.append(parse_project(project.parent))
		else: 
			#there are no more pages
			stop = True
		page += 1

	return projects
	#return [parse_project(project.parent) ]

def download_file(url, path):
	f = urlopen(url)
	out = open(path, "wb")
	out.write(f.read())
	out.close()

def download_project(project, outputdir):
	if ("apk_url" in project):
		#save apk
		filename = os.path.join(outputdir, project["id"] + ".apk")
		download_file(project["apk_url"], filename)

	if ("source_url" in project):
		#save source files
		filename = os.path.join(outputdir, project["id"] + ".tar.gz")
		download_file(project["source_url"], filename)

def save_file(project, outputdir):
	file_path = os.path.join(outputdir, "info.txt")
	f = open(file_path, "w")
	keys = ["id", "title", "description", "apk_url", "source_url"]
	for key in keys:
		if key in project:
			f.write(key + " = " + project[key] + "\n")
	f.close()

def save_project(project, outputdir):
	#first create the directory for the app
	print "Saving project " + project['title'] + " (" + project['id'] + ") ..."
	appdir = os.path.join(outputdir, project["id"])
	if not os.path.isdir(appdir):
		os.mkdir(appdir)
	#save info file, apk and source
	save_file(project, appdir)
	download_project(project, appdir)

def save_projects(projects, outputdir):
	for project in projects:
		save_project(project, outputdir)

URL = "https://f-droid.org/repository/browse/?fdcategory={0}&fdpage={1}"

if (len(sys.argv) < 4):
    print "Usage: python scraper.py <category> <numberapps> <outputdir> [<page>]"
    print "\t- <category>: category in the fdroid repository"
    print "\t- <numberapps>: number of apps to download"
    print "\t- <outputdir>: Directory where the apps are going to be saved"
    print "\t- <page>: starting page (optional)"
    sys.exit(1)

category = sys.argv[1]  
numberapps = int(sys.argv[2])
outputdir = sys.argv[3]
page = 1
if (len(sys.argv) > 4):
	page = int(sys.argv[4])

save_projects(get_projects(URL, page, category, numberapps), outputdir)
