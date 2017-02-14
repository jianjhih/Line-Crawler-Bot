#encoding=UTF-8

from flask import Flask, request, abort
import requests
import json 
import re
from bs4 import BeautifulSoup as bs
from aenum import Enum

requests.packages.urllib3.disable_warnings()

class Options(Enum):
	dic = 1
	beauty = 2
	eyny = 3
	news = 4
	ptthot = 5
	movie = 6
	technews = 7
	panx = 8
	help = 9

# 可以直接利用Line提供的SDK來處理
# from linebot import LineBotApi
# from linebot.models import TextSendMessage

app = Flask(__name__)

tasks = [
	{
		'id': 1,
		'title': u'Buy groceries',
		'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
		'done': False
	},
	{
		'id': 2,
		'title': u'Learn Python',
		'description': u'Need to find a good Python tutorial on the web', 
		'done': False
	}
]

# 測試Restful GET
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
	return json.dumps({'tasks': tasks})
	
# 測試Restful GET 帶參數
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return json.dumps({'task': task[0]})
	
# 測試Restful POST
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	tasks.append(task)
	return json.dumps({'task': task}), 201
	
# 測試Restful PUT
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return json.dumps({'task': task[0]})
	
# 測試Restful DELETE
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return json.dumps({'result': True})
	
# 測試app.py有沒有Deploy成功
@app.route("/", methods=["GET"])
def index():
	return "hello world >>> index", 200
	
# 在Line的Document當中有寫到，webhook URL會透過post request呼叫 https://{urladdress}/callback
@app.route("/callback", methods=["POST"])
def callback():
	temp = request.get_json()
	for i in temp['events']:		
		ttt = i['replyToken']
		print i['source']['userId']
		if i['message']['type']=='text':
			msg = i['message']['text']
		replyapi(ttt, msg)
	return "hello world >>> callback", 200
	
def getPageNumber(content):
	startIndex = content.find('index')
	endIndex = content.find('.html')
	pageNumber = content[startIndex + 5: endIndex]
	return pageNumber
	
def crawPage(url, push_rate):
	rs = requests.session()
	res = rs.get(url, verify=False)
	soup = bs(res.text, 'html.parser')
	for r_ent in soup.find_all(class_="r-ent"):
		try:
			# 先得到每篇文章的篇url
			link = r_ent.find('a')['href']
			if 'M.1430099938.A.3B7' in link:
				continue
			comment_rate = ""
			if (link):
				# 確定得到url再去抓 標題 以及 推文數
				title = r_ent.find(class_="title").text.strip()
				rate = r_ent.find(class_="nrec").text
				URL = 'https://www.ptt.cc' + link
				if (rate):
					comment_rate = rate
					if rate.find(u'爆') > -1:
						comment_rate = 100
					if rate.find('X') > -1:
						comment_rate = -1 * int(rate[1])
				else:
					comment_rate = 0
				# 比對推文數
				if int(comment_rate) >= push_rate:
					article_list.append((int(comment_rate), URL, title))
		except:
			# print u'crawPage function error:',r_ent.find(class_="title").text.strip()
			# print('本文已被刪除')
			print 'delete'
			
article_list = []
			
def pttBeauty():
	rs = requests.session()
	res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
	soup = bs(res.text, 'html.parser')
	ALLpageURL = soup.select('.btn.wide')[1]['href']
	start_page = int(getPageNumber(ALLpageURL)) + 1
	page_term = 3  # crawler count
	push_rate = 10  # 推文
	index_list = []
	for page in range(start_page, start_page - page_term, -1):
		page_url = 'https://www.ptt.cc/bbs/Beauty/index' + str(page) + '.html'
		index_list.append(page_url)
		
	# 抓取 文章標題 網址 推文數
	while index_list:
		index = index_list.pop(0)
		res = rs.get(index, verify=False)
		soup = bs(res.text, 'html.parser')
		# 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
		if (soup.title.text.find('Service Temporarily') > -1):
			index_list.append(index)
			# print u'error_URL:',index
			# time.sleep(1)
		else:
			crawPage(index, push_rate)
			# print u'OK_URL:', index
			# time.sleep(0.05)
	content = ''
	for article in article_list:
		data = "[" + str(article[0]) + "] push" + article[2] + "\n" + article[1] + "\n\n"
		content += data
	return content
	
def patternMega(text):
	patterns = ['mega', 'mg', 'mu', 'ＭＥＧＡ', 'ＭＥ', 'ＭＵ', 'ｍｅ', 'ｍｕ', 'ｍｅｇａ']
	for pattern in patterns:
		if re.search(pattern, text, re.IGNORECASE):
			return True
	
def eynyMovie():
	targetURL = 'http://www.eyny.com/forum-205-1.html'
	rs = requests.session()
	res = rs.get(targetURL, verify=False)
	soup = bs(res.text, 'html.parser')
	content = ''
	for titleURL in soup.select('.bm_c tbody .xst'):
		if (patternMega(titleURL.text)):
			title = titleURL.text
			if '10990869-1-3' in titleURL['href']:
				continue
			link = 'http://www.eyny.com/' + titleURL['href']
			data = title + '\n' + link + '\n\n'
			content += data
	return content
	
def appleNews():
	targetURL = 'http://www.appledaily.com.tw/realtimenews/section/new/'
	head = 'http://www.appledaily.com.tw'
	rs = requests.session()
	res = rs.get(targetURL, verify=False)
	soup = bs(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('.rtddt a'), 0):
		if index == 15:
			return content
		if head in data['href']:
			link = data['href']
		else:
			link = head + data['href']
		content += link + '\n\n'
	return content
	
def pttHot():
	targetURL = 'http://disp.cc/b/PttHot'
	rs = requests.session()
	res = rs.get(targetURL, verify=False)
	soup = bs(res.text, 'html.parser')
	content = ""
	for data in soup.select('#list div.row2 div span.listTitle'):
		title = data.text
		link = "http://disp.cc/b/" + data.find('a')['href']
		if data.find('a')['href'] == "796-59l9":
			break
		content += title + "\n" + link + "\n\n"
	return content
	
def movie():
	targetURL = 'http://www.atmovies.com.tw/movie/next/0/'
	rs = requests.session()
	res = rs.get(targetURL, verify=False)
	res.encoding = 'utf-8'
	soup = bs(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('ul.filmNextListAll a')):
		if index == 20:
			return content
		title = data.text.replace('\t', '').replace('\r', '')
		link = "http://www.atmovies.com.tw" + data['href']
		content += title + "\n" + link + "\n"
	return content
	
def technews():
	targetURL = 'https://technews.tw/'
	rs = requests.session()
	res = rs.get(targetURL, verify=False)
	res.encoding = 'utf-8'
	soup = bs(res.text, 'html.parser')
	content = ""
	
	for index, data in enumerate(soup.select('article div h1.entry-title a')):
		if index == 12:
			return content
		title = data.text
		link = data['href']
		content += title + "\n" + link + "\n\n"
	return content
	
def panx():
	targetURL = 'https://panx.asia/'
	rs = requests.session()
	res = rs.get(targetURL, verify = False)
	soup = bs(res.text, 'html.parser')
	content = ""
	for data in soup.select('div.container div.row div.desc_wrap h2 a'):
		title = data.text
		link = data['href']
		content += title + "\n" + link + "\n\n"
	return content
	
def yahooDic(msg):
	ret = ''
	a = msg.split(" ")
	res = requests.get('http://tw.dictionary.search.yahoo.com/search?p=' + a[1])
	soup = bs(res.content, 'html.parser')
	uls = soup.find_all('ul', attrs = {'class':'compArticleList mb-15 ml-10'})
	for ul in uls:
		ret += (ul.text.encode('utf-8') + '\n')
	return ret
	
def processMessage(msg):
	ret = []
	mat = []
	pat = re.compile(r".*(掰掰).*")
	mat = pat.findall(msg)
	if len(mat) == 0:
		ret.append('朕知道了')
		ret.append('可以退下了')
	else:
		ret.append('慢走不送')
	return ret
	
def parseKeyword(msg):
	ret = ''
	pat = re.compile("@(.*)")
	mat = pat.findall(msg)
	if len(mat) == 0:
		return ''
	return mat[0]
	
def genData(accesstoken, msgs):
	data = [];
	for msg in msgs:
		data.append({'type':'text', 'text':msg})
	ret = {
	'replyToken':accesstoken,
	'messages':data
	}
	return ret
	
def genHeaders(channeltoken):
	ret = {
		'Content-Type':'application/json',
		'Authorization':'Bearer ' + channeltoken
	}
	return ret

def genHelpData():
	arr = ['"@beauty":ptt 表特版近期大於 10 推的文章',
	'"@eyny":eyny 電影版 Mega 連結的網址',
	'"@news":apple news 即時新聞',
	'"@ptthot":ptt 近期熱門的文章',
	'"@movie":近期上映的電影 ( 開眼電影網 )',
	'"@technews":科技新聞',
	'"@panx":科技新聞 ( 泛科技 ) ',
	'"dic {word}":透過{word}查找yahoo字典',
	'"help":教學說明']
	ret = ';\n'.join(arr)
	return ret 
	
def replyapi(accesstoken, msg):
	channeltoken='channel token'
	
	# 利用Line SDK的方式，做reply的作業。	
	"""
	line_bot_api = LineBotApi(channeltoken)
	
	try:
		line_bot_api.reply_message(accesstoken, TextSendMessage(text='Hello World!'))
	except linebot.LineBotApiError as e:
		print e
		# error handle
		
	"""
	
	t = msg.encode('utf-8')
	data = {}
	
	if '@' in t:
		if Options.beauty.name in parseKeyword(t):
			data = genData(accesstoken, [pttBeauty()])
		elif Options.eyny.name in parseKeyword(t):
			data = genData(accesstoken, [eynyMovie()])
		elif Options.ptthot.name in parseKeyword(t):
			data = genData(accesstoken, [pttHot()])
		elif Options.movie.name in parseKeyword(t):
			data = genData(accesstoken, [movie()])
		elif Options.technews.name in parseKeyword(t):
			data = genData(accesstoken, [technews()])
		elif Options.news.name in parseKeyword(t):
			data = genData(accesstoken, [appleNews()])
		elif Options.panx.name in parseKeyword(t):
			data = genData(accesstoken, [panx()])
		else:
			data = genData(accesstoken, ['沒有這個功能~'])
	else:
		if Options.dic.name in t:
			data = genData(accesstoken, [yahooDic(t)])
		elif Options.help.name == t:
			data = genData(accesstoken, [genHelpData()])
		else:
			data = genData(accesstoken, processMessage(t))

	headers = genHeaders(channeltoken)
	
	urladdress = 'https://api.line.me/v2/bot/message/reply'
	datajson = json.dumps(data)
	# 依照Line Document當中的定義，準備好headers和data(json格式)。
	res = requests.post(urladdress, headers = headers, data = datajson)


if __name__=='__main__':
	app.run()
