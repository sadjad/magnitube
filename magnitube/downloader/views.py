from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from formats import FORMATS

import urlparse
import subprocess as sub
import re
import urllib2



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
	
	return render(request, "downloader/download_links.html", {'links': links, 'video_id': video_id, 'formats': FORMATS})	
	

def download(request, video_id, id):
	id = int(id)
	links = request.session['links']
	url = links[id][0]
	
	if 'video_id' not in request.session or video_id != request.session['video_id']:
		return HttpResponseRedirect('/%s/' % video_id)
		
	test_request = urllib2.Request("http://%s" % url)
	test_request.get_method = lambda: 'HEAD'
	test_response = urllib2.urlopen(test_request)
	
	if test_response.getcode() / 100 == 3 and test_response.headers.has_key('Location'):
		url = test_response.headers.getheader('Location').replace('http://', '')	
	
	response = HttpResponse()
	response['Content-Type'] = 'application/octet-stream'
	response['Content-Disposition'] = 'attachment; filename="%s"' % links[id][1]
	response['X-Accel-Redirect'] = "/download/%s/%s" % ("/".join(url.split("?")), links[id][1])
	response['X-Accel-Limit-Rate'] = '100k'
	
	return response
	
	