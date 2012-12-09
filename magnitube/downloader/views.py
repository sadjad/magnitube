from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from formats import FORMATS

import urlparse
import subprocess as sub
import re
import urllib2
import httplib


def index(request):
	return render(request, "downloader/index.html", {})
	
def process_download_request(request):
	if request.method == 'POST' and 'url' in request.POST:
		url = request.POST['url'].strip()
		url_data = urlparse.urlparse(url)
		url_qs = urlparse.parse_qs(url_data.query)
		
		if 'v' in url_qs and re.match('^[-\w]+$', url_qs['v'][0]):
			video_id = url_qs['v'][0]
			return HttpResponseRedirect('/%s/' % video_id)
		
	return render(request, "downloader/index.html", {})	

def show_list(request, video_id):
	p = sub.Popen(["youtube-dl", "--all-formats", "-g", "--get-format", "--get-filename",
		"http://www.youtube.com/watch?v=%s" % video_id],
		stdout=sub.PIPE,
		stderr=sub.PIPE)
	
	output, errors = p.communicate()
	output = output.split('\n')

	links = {}
	
	for i in range(len(output) / 3):
		links[int(output[3*i + 2])] = [output[3*i].replace("http://", ""), output[3*i + 1]]
	
	request.session['links'] = links
	request.session['video_id'] = video_id
	
	sorted_links = sorted(links.iteritems(), key=lambda a: FORMATS[a[0]]['resolution'])
	current_fmts = [fmt for fmt, link in sorted_links]
	
	if 18 in current_fmts:
		current_fmt = 18
	elif 43 in current_fmts:
		current_fmt = 43
	elif 34 in current_fmts:
		current_fmt = 34
	elif 5 in current_fmts:
		current_fmt = 5
	elif 6 in current_fmts:
		current_fmt = 6
	else:
		current_fmt = current_fmts[0]
		
	current_filename = links[current_fmt][1]
		
	
	return render(request, "downloader/download_links.html", {'links': sorted_links, 'video_id': video_id, 'formats': FORMATS, 'current_fmt': current_fmt, 'current_filename': current_filename})	
	
def view(request, video_id, fmt):
	fmt = int(fmt)
	links = request.session['links']	
	if 'video_id' not in request.session or video_id != request.session['video_id']:
		return HttpResponseRedirect('/%s/' % video_id)
		
	filename = links[fmt][1]
	return render(request, "view.html", locals())

def download(request, video_id, id):
	id = int(id)
	links = request.session['links']
	url = links[id][0]
	
	if 'video_id' not in request.session or video_id != request.session['video_id']:
		return HttpResponseRedirect('/%s/' % video_id)
		
	conn = httplib.HTTPConnection(url.split("/")[0])
	conn.request("HEAD", "/%s" % url.split("/")[1])
	test_response = conn.getresponse()
	
	if (test_response.status / 100) == 3 and test_response.getheader('Location', None):
		url = test_response.getheader('Location').replace('http://', '')
	
	response = HttpResponse()
	
	if 'view' not in request.GET:
		response['Content-Type'] = 'application/octet-stream'
		response['Content-Disposition'] = 'attachment; filename="%s"' % links[id][1]
		
	response['X-Accel-Redirect'] = "/download/%s/%s" % ("/".join(url.split("?")), links[id][1])
	
	return response
	
	