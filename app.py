#encoding=UTF-8

from flask import Flask, request, abort
from flask_pymongo import PyMongo
#from flask.ext.pymongo import PyMongo
from datetime import datetime
import requests
import json 
import re
from bs4 import BeautifulSoup as bs
from aenum import Enum
import random
from bson.json_util import dumps
from bson.json_util import loads 
import sys
import time

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

app.config['MONGO_DBNAME'] = 'linebot'
app.config['MONGO_URI'] = 'mongodb://linebot:123456@ds015892.mlab.com:15892/linebot'
mongo = PyMongo(app)

app.config['MONGO2_DBNAME'] = 'googlemapapp'
app.config['MONGO2_URI'] = 'mongodb://admin:123456@ds111940.mlab.com:11940/googlemapapp'
mongo2 = PyMongo(app, config_prefix='MONGO2')

# GoogleMap mongodb users 的insert
@app.route('/addusers/<string:account>/<string:pwd>/<string:name>', methods=['GET'])
def addusers(account, pwd, name):
	users = mongo2.db.users
	result = users.insert({'Account':account, 'UserName':name, 'PassWord':pwd, 'Count':0})
	return dumps(result)
	
# GoogleMap mongodb users 的update
@app.route('/updateUsersCount/<string:account>', methods=['GET'])
def updateUsersCount(account):
	num = updateUsersCountFunc(account)
	if num == 0:
		return 'Update Users Fail'
	return 'Update Users Succeed'
	
def updateUsersCountFunc(account):
	users = mongo2.db.users
	
	list = users.find({'Account':account})
	if list.count() == 0:
		return 0
		
	result = users.update_one({
	'_id': list[0]['_id']
	},{
	  '$set': {
		'Count': list[0]['Count'] + 1
	  }
	}, upsert=False)
	
	return result.matched_count
	
# GoogleMap mongodb users 的query
@app.route('/queryCurrentUsersCount/<string:account>', methods=['GET'])
def queryCurrentUsersCount(account):
	users = mongo2.db.users
	
	list = users.find({'Account':account})
	if list.count() == 0:
		return json.dumps({'Response' : 0})
	return json.dumps({'Response' : list[0]['Count']})
	
# GoogleMap mongodb users 的 update 和 star 的 delete
@app.route('/deleteStarsAndUpdateUsersCount/<string:account>/<float:latitude>/<float:longitude>', methods=['GET'])
def deleteStarsAndUpdateUsersCount(account, latitude, longitude):
	deleteNum = deleteStarFunc(latitude, longitude)
	if deleteNum == 0:
		return json.dumps({'Response' : 0})
	updateNum = updateUsersCountFunc(account)
	if updateNum == 0:
		return json.dumps({'Response' : 0})
	return json.dumps({'Response' : 1})
	
# GoogleMap mongodb star 的insert
@app.route('/addstar', methods=['GET'])
def addstar():
	RequestID = genStarRequestID() + 1
	stars = mongo2.db.stars
	result = stars.insert(genstar(RequestID))
	return dumps(result)

# GoogleMap mongodb star 的insert
@app.route('/addstars/<int:num>', methods=['GET'])
def addstars(num):
	RequestID = genStarRequestID() + 1
	stars = mongo2.db.stars
	arr = []
	for i in range(1, num + 1, 1):
		arr.append(genstar(RequestID))
		RequestID = RequestID + 1
	stars.insert_many(arr)
	return ''.join(['Add ', str(num) , ' Stars'])
	
def genStarRequestID():
	stars = mongo2.db.stars
	list = stars.find().sort('RequestID', -1)
	if list.count() == 0:
		return 0
	return list[0]['RequestID']
	
def genstar(RequestID):
	randPoint = random.randint(1, 3)
	randLatitude = random.uniform(21.54, 25.18)
	randLongitude = random.uniform(120.04, 121.59)
	return {'latitude':randLatitude, 'longitude':randLongitude, 'point':randPoint, 'CreateDate':datetime.now(), 'RequestID':RequestID}
	
# GoogleMap mongodb star 的delete
@app.route('/deleteStar/<float:latitude>/<float:longitude>', methods=['GET'])
def deleteStar(latitude, longitude):
	ret = str(deleteStarFunc(latitude, longitude))
	return ret
	
def deleteStarFunc(latitude, longitude):
	stars = mongo2.db.stars
	result = stars.delete_many({'latitude':latitude, 'longitude':longitude,})
	return result.deleted_count
	
# GoogleMap mongodb star 的query
@app.route('/getAllStars', methods=['GET'])
def getAllStars():
	stars = mongo2.db.stars
	return ''.join(['{\"Response\" : ', dumps(stars.find()), '}'])
	
# 躺躺喵 mongodb learntalk 的insert
@app.route('/addlearntalk', methods=['GET'])
def addlearntalk():
	addlearntalk('test', '456');
	return 'Add learntalk'
	
def addlearntalk(KeyWord, Content):
	learntalk = mongo.db.learntalk
	learntalk.insert({'KeyWord':KeyWord, 'Response':Content, 'CreateDate':datetime.now()})
	
# 躺躺喵 mongodb learntalk 的delete
@app.route('/deletelearntalk/<string:keyword>', methods=['GET'])
def deletelearntalk(keyword):
	learntalk = mongo.db.learntalk
	learntalk.delete_many({"_id": learntalk.find({'KeyWord':keyword}).sort('CreateDate', -1)[0]['_id']})
	return 'Delete learntalk'
	
# 躺躺喵 mongodb learntalk 的query
@app.route('/getlearntalk/<string:keyword>', methods=['GET'])
def getlearntalk(keyword):
	learntalk = mongo.db.learntalk
	ret = ''
	list = learntalk.find({'KeyWord':keyword}).sort('CreateDate', -1)
	if list.count() == 0:
		return json.dumps({'Response' : ret})
	return json.dumps({'Response' : list[0]['Response']})
	
# 躺躺喵 mongodb JCBUser 的insert
@app.route('/addJCBUser', methods=['GET'])
def addJCBUser():
	JCBUser = mongo.db.JCBUser
	JCBUser.insert({'Name':'1', 'txtCreditCard1':'2', 'txtCreditCard2':'3', 'txtCreditCard4':'4', 'txtEasyCard1':'5', 'txtEasyCard2':'6', 'txtEasyCard3':'7', 'txtEasyCard4':'8', 'CreateDate':datetime.now()})
	return 'Add JCBUser'
	
# 躺躺喵 mongodb JCBUser 的query
@app.route('/getJCBUser/<string:name>', methods=['GET'])
def getJCBUser(name):
	JCBUser = mongo.db.JCBUser
	ret = ''
	list = JCBUser.find({'Name':name})
	if list.count() == 0:
		return json.dumps({'Response' : ret})
	return ''.join(['{\"Response\" : ', dumps(list[0]), '}'])
	
def findJCBUser(name):
	JCBUser = mongo.db.JCBUser
	list = JCBUser.find({'Name':name})
	if list.count() == 0:
		return 0
	return list[0]
	
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
	
def JCBQuery(name):
	JCBUser = findJCBUser(name)
	
	if JCBUser == 0:
		return 'N/R'
	
	ret = []
	count = 0
	while True:
		try:
			# parse time stamp and captcha
			s = requests.Session()
			res = s.get('https://ezweb.easycard.com.tw/Event01/captcha_A', verify = False)
			soup = bs(res.text, "html.parser")
			res2 = soup.select('script')[0]
			# parse time stamp
			m = re.search('setCaptcha\(\'(.*)\'\)', res2.text)
			ret.append(''.join(['time stamp:', m.group(1)]))
			
			# parse captcha
			m2 = re.search('setCP\(\'(.*)\'\)', res2.text)
			ret.append(''.join(['captcha:', m2.group(1)]))
			
			# read EasyCard number
			txtEasyCard1 = JCBUser['txtEasyCard1']
			txtEasyCard2 = JCBUser['txtEasyCard2']
			txtEasyCard3 = JCBUser['txtEasyCard3']
			txtEasyCard4 = JCBUser['txtEasyCard4']
			
			# post parameters
			payload = {'txtEasyCard1':txtEasyCard1,
			'txtEasyCard2':txtEasyCard2,
			'txtEasyCard3':txtEasyCard3,
			'txtEasyCard4':txtEasyCard4,
			'captcha':m2.group(1),
			'method':'queryLoginDate',
			'hidCaptcha':m.group(1)}
			
			# show query result
			res1 = s.post('https://ezweb.easycard.com.tw/Event01/JCBLoginRecordServlet', data = payload)
			# print res1.text
			soup2 = bs(res1.text, "html.parser")
			# show card number
			ret.append(soup2.select('.card_num')[0].text)
			res3 = soup2.select('.step2')
			# show data
			for r in res3[0].select('tr'):
				if len(r.select('td')) > 0 :
					ret.append(''.join([r.select('td')[0].text.strip(), r.select('td')[1].text.strip()]))
					
			if len(res3[0].select('tr')) > 0:
				ret.append(''.join(['retry count:', str(count)]))
				break
				
		except Exception as e:
			count = count + 1
			time.sleep(5) # delays for 5 seconds
			
	return '\n'.join(ret)
	
def JCBLogin(name):
	JCBUser = findJCBUser(name)
	
	if JCBUser == 0:
		return 'N/R'
	
	ret = []
	count = 0
	while True:
		try:
			# parse time stamp and captcha
			s = requests.Session()
			res = s.get('https://ezweb.easycard.com.tw/Event01/captcha_A', verify = False)
			soup = bs(res.text, "html.parser")
			res2 = soup.select('script')[0]
			# parse time stamp
			m = re.search('setCaptcha\(\'(.*)\'\)', res2.text)
			ret.append(''.join(['time stamp:', m.group(1)]))
			# parse captcha
			m2 = re.search('setCP\(\'(.*)\'\)', res2.text)
			ret.append(''.join(['captcha:', m2.group(1)]))
			
			# read EasyCard and CreditCard number
			txtEasyCard1 = JCBUser['txtEasyCard1']
			txtEasyCard2 = JCBUser['txtEasyCard2']
			txtEasyCard3 = JCBUser['txtEasyCard3']
			txtEasyCard4 = JCBUser['txtEasyCard4']
			txtCreditCard1 = JCBUser['txtCreditCard1']
			txtCreditCard2 = JCBUser['txtCreditCard2']
			txtCreditCard4 = JCBUser['txtCreditCard4']
			
			# post parameters
			payload = {
			'accept':'',
			'txtCreditCard1':txtCreditCard1,
			'txtCreditCard2':txtCreditCard2,
			'txtCreditCard4':txtCreditCard4,
			'txtEasyCard1':txtEasyCard1,
			'txtEasyCard2':txtEasyCard2,
			'txtEasyCard3':txtEasyCard3,
			'txtEasyCard4':txtEasyCard4,
			'captcha':m2.group(1),
			'method':'loginAccept',
			'hidCaptcha':m.group(1),
			'CP':m2.group(1)
			}
			
			# request headers
			headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
			'Cache-Control':'max-age=0',
			'Connection':'keep-alive',
			'Content-Length':'216',
			'Content-Type':'application/x-www-form-urlencoded',
			'Cookie':'JSESSIONID=EE27D568BECAD4D3D144C53280735188',
			'Host':'ezweb.easycard.com.tw',
			'Origin':'https://ezweb.easycard.com.tw',
			'Referer':'https://ezweb.easycard.com.tw/Event01/JCBLoginServlet',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
			}
			
			res3 = s.post('https://ezweb.easycard.com.tw/Event01/JCBLoginServlet', data = payload)
			soup2 = bs(res3.text, "html.parser")
			if len(soup2.select('#content')) > 0 :
				ret.append(soup2.select('#content')[0].text)
				ret.append(''.join(['retry count:', str(count)]))
				break
		except Exception as e:
			count = count + 1
			time.sleep(5) # delays for 5 seconds
	
	return '\n'.join(ret)
	
def processMessage(msg):
	ret = []
	mat = []
	
	response = getlearntalk(msg)
	jsonData = json.loads(response)
	if len(jsonData['Response']) != 0:
		ret.append(jsonData['Response'])
		return ret
	
	pat = re.compile(r".*(掰掰).*")
	mat = pat.findall(msg)
	
	if len(mat) == 0:
		ret.append('朕知道了')
		ret.append('可以退下了')
	else:
		ret.append('慢走不送')
		
	return ret
	
def learnTalkFunc(msg):
	ret = []
	
	msg_learnTalk = unicode(msg, 'utf-8')
	
	flag = True # 紀錄是否要執行 addlearntalk()
	
	mat2 = []
	pat2 = re.compile(ur"躺躺喵[;|；]忘記[;|；](.*)")
	mat2 = pat2.findall(msg_learnTalk)
	if len(mat2) != 0:
		deletelearntalk(mat2[0])
		ret.append('我最聽話~~')
		flag = False
	
	if flag :
		mat1 = []
		pat1 = re.compile(ur"躺躺喵[;|；](.*)[;|；](.*)")
		mat1 = pat1.findall(msg_learnTalk)
		if len(mat1) != 0:
			addlearntalk(mat1[0][0], mat1[0][1])
			ret.append('好哦~好哦~')
	
	return ret
	
def JCBFunc(msg):
	ret = []
	
	msg_JCB = unicode(msg, 'utf-8')
	
	flag = True # 紀錄是否要執行 JCBLogin
	
	mat2 = []
	pat2 = re.compile(ur"JCB[;|；]查詢[;|；](.*)")
	mat2 = pat2.findall(msg_JCB)
	if len(mat2) != 0:
		ret.append(JCBQuery(mat2[0]))
		flag = False
	
	if flag :
		mat1 = []
		pat1 = re.compile(ur"JCB[;|；]登錄[;|；](.*)")
		mat1 = pat1.findall(msg_JCB)
		if len(mat1) != 0:
			ret.append(JCBLogin(mat1[0]))
			
	return ret
	
def isTalkFormat(msg):
	mat = []
	pat = re.compile(r"躺躺喵[;|；].*[;|；].*")
	mat = pat.findall(msg)
	if len(mat) == 0:
		return False
	return True
	
def isJCBFormat(msg):
	mat = []
	pat = re.compile(r"JCB[;|；].*[;|；].*")
	mat = pat.findall(msg)
	if len(mat) == 0:
		return False
	return True
	
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
	'"help":教學說明', 
	'躺躺喵學說話:躺躺喵；{關鍵字}；{回應}',
	'躺躺喵忘記說話:躺躺喵；忘記；{關鍵字}']
	ret = ';\n'.join(arr)
	return ret 
	
def replyapi(accesstoken, msg):
	channeltoken='qYzIzIqCTWz82oZkTnO0A9Ggiz6bNkS1VHIMU/9kCww/M709Ff+PFDObSL+OFvhSQlLpYlTDmxkKgKS2SwbkoZs/tLEgzLlJYY+Wsf1yB6J//rQfZOuv9dLeCpt2fcBg984pT1wLpBT0uNEcmBuAaQdB04t89/1O/w1cDnyilFU='
	
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
		elif isTalkFormat(t):
			data = genData(accesstoken, learnTalkFunc(t))
		elif isJCBFormat(t):
			data = genData(accesstoken, JCBFunc(t))
		else:
			data = genData(accesstoken, processMessage(t))
		
	headers = genHeaders(channeltoken)
	urladdress = 'https://api.line.me/v2/bot/message/reply'
	datajson = json.dumps(data)
	# 依照Line Document當中的定義，準備好headers和data(json格式)。
	res = requests.post(urladdress, headers = headers, data = datajson)


if __name__=='__main__':
	app.run()