import re
import copy

import execjs
import requests

requests.packages.urllib3.disable_warnings()

login_headers = {
	"Host":"zj.ac.10086.cn",
	"Upgrade-Insecure-Requests":"1",
	"Content-Type":"application/x-www-form-urlencoded",
	"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	}

info_headers = {
	"Host":'www.zj.10086.cn',
	"Upgrade-Insecure-Requests":"1",
	"Content-Type":"application/x-www-form-urlencoded",
	"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	}

service_headers = {
	"Host":'service.zj.10086.cn',
	"Upgrade-Insecure-Requests":"1",
	"Content-Type":"application/x-www-form-urlencoded",
	"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	}


def login():	
	"""登录函数"""

	# 获取js执行对象
	with open('encrypt.js',encoding='utf-8') as f:
		js = f.read()
	ctx = execjs.compile(js)
	

	# # 登录手机号
	moblile = input("input your phone ....")
	# 登录密码 
	password = input("input your service password ....")
	# 记录cookie
	cookies = dict()


	# 1 首页，获取cookie(JSESSIONID)
	url = 'https://zj.ac.10086.cn/login'
	resp = requests.get(url,headers=login_headers,verify=False)
	# 此参数用于登录1
	spid = re.search(r'id="spid" value="(.+?)"', resp.text).group(1)
	cookies.update(resp.cookies.get_dict())

	# 2 获取图像验证码
	url = 'https://zj.ac.10086.cn/common/image.jsp'
	resp = requests.get(url,headers=login_headers,cookies=cookies,verify=False)
	with open('captcha.jpg','wb') as f:
		f.write(resp.content)
	cookies.update(resp.cookies.get_dict())

	# 3 输入验证码,错误的话返回
	captcha_code = input('please input captcha....')
	url = f'https://zj.ac.10086.cn/validImageCode?r_0.23228170808194792&imageCode={captcha_code}'
	resp = requests.get(url,headers=login_headers,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())
	if resp.text.find('1') == -1:
		print('error captcha input - -')
		return False

	# 4 登录一
	url = 'https://zj.ac.10086.cn/Login'
	data = {
	"type":"B",
	"spid":spid,
	"mobileNum":ctx.call("enString",moblile),
	"validCode":captcha_code,
	"servicePassword":ctx.call("enString",password),
	}
	resp = requests.post(url,headers=login_headers,data=data,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())
	# 此两个参数用于登录二
	SAMLart = re.search(r'name="SAMLart" value="(.+?)"',resp.text).group(1)
	displayPics = re.search(r'name="displayPics" value="(.+?)"',resp.text).group(1)

	# 5 登录二
	url = 'https://zj.ac.10086.cn/login/backPage.jsp'
	data = {
		"AppSessionId":"NotExist",
		"SAMLart":SAMLart,
		"isEncodePassword":"2",
		"displayPic":"1",
		"isEncodeMobile":"2",
		"displayPics":displayPics,
	}
	resp = requests.post(url,headers=login_headers,data=data,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())

	# 6 登录三,登录重定向到登录成功的页面
	# 更新 headers
	url = 'http://www.zj.10086.cn/my/servlet/assertion'
	data = {
	"RelayState":"type=B;backurl=http://www.zj.10086.cn/my/servlet/assertion;nl=6;loginFromUrl=http%3A%2F%2Fwww.zj.10086.cn%2Fmy%2Findex.do;callbackurl=/servlet/assertion;islogin=true",
	"SAMLart":SAMLart,
	}
	# 禁止重定向，以便获取重定向前有用的cookie
	resp = requests.post(url,headers=info_headers,data=data,cookies=cookies,allow_redirects=False,verify=False)
	cookies.update(resp.cookies.get_dict())
	# 登录成功后的重定向地址
	Location = resp.headers.get('Location')

	# 7 登录成功返回cookie
	# 登录成功时,状态码为302，重定向的Location为 http://www.zj.10086.cn/my/index.do
	if resp.status_code == 302 and Location.find('http://www.zj.10086.cn/my/index.do') !=-1:
		# 返回登录成功的cookie
		return cookies


def crawl(cookies):
	"""爬虫函数"""

	# # ========== 爬取个人信息 =========
	print('==========个人信息=====\n\n\n\n')
    # 星级等信息
	url = 'http://www.zj.10086.cn/my/findUserInfos.do?AISSO_LOGIN=true'
	resp = requests.post(url,cookies=cookies,headers=info_headers,verify=False)
	print(resp.text)

	# 当月话费
	url = 'http://www.zj.10086.cn/my/queryAccountAndCostInfo.do?AISSO_LOGIN=true'
	resp = requests.post(url,cookies=cookies,headers=info_headers,verify=False)
	print(resp.text)    

	# 套餐等个人信息
	url = 'http://www.zj.10086.cn/my/queryKtbbinfoqry.do?AISSO_LOGIN=true'
	resp = requests.get(url,cookies=cookies,headers=info_headers,verify=False)
	print(resp.text)   

	# 充值信息
	# 得到 bid ,mobileno
	pay_cookies = copy.deepcopy(cookies)
	url = 'http://www.zj.10086.cn/my/login/zjehallLogin.do?urlFlag=7&AISSO_LOGIN=true'
	resp = requests.get(url,headers=info_headers,cookies=pay_cookies,verify=False)
	pay_cookies.update(resp.cookies.get_dict())
	bid = re.search(r'name="bid" value="(.+?)"',resp.text).group(1)
	mobileno = re.search(r'name="mobileno" value="(.+?)"',resp.text).group(1)
	# 查询充值信息
	url = f'http://service.zj.10086.cn/inline/my/rechargeQuery.do?bid={bid}&mobileno={mobileno}&yearmonth=201901'
	data = {"yearmonth":"201901"}
	resp = requests.get(url,headers=service_headers,cookies=pay_cookies,verify=False)
	print(resp.text)



	# ========== 爬取每月账单 ==========
	print('==========账单=====\n\n\n\n')
	bill_cookies = copy.deepcopy(cookies)
	# 获取账单表单id
	url = 'http://service.zj.10086.cn/yw/myBillAnalysis/myBillAnalysisQuery.do?menuId=13003'
	resp = requests.get(url,headers=service_headers,cookies=bill_cookies,verify=False)	
	SAMLRequest = re.search(r'name="SAMLRequest" value="([\s\S]+?)"',resp.text).group(1).replace('\n','')
	RelayState = re.search(r'name="RelayState" value="(.+?)"',resp.text).group(1)
	bill_cookies.update(resp.cookies.get_dict())

	# 详单账单id登录
	url = 'https://zj.ac.10086.cn/POST'
	data = {'SAMLRequest':SAMLRequest,'RelayState':RelayState}
	resp = requests.post(url,headers=service_headers,data=data,cookies=bill_cookies,verify=False)
	bill_cookies.update(resp.cookies.get_dict())
	SAMLart = re.search(r'name="SAMLart" value="(.+?)"',resp.text).group(1)
	RelayState = re.search(r'name="RelayState" value="(.+?)"',resp.text).group(1)

	# 详单账单重定向
	url = 'http://service.zj.10086.cn/servlet/assertion'
	data = {
	"AppSessionId":"NotExist",
	"SAMLart":SAMLart,
	"isEncodePassword":"2",
	"displayPic":"0",
	"RelayState":RelayState,
	"isEncodeMobile":"2",
	}
	resp = requests.post(url,headers=service_headers,data=data,cookies=bill_cookies,allow_redirects=False,verify=False)
	bill_cookies.update(resp.cookies.get_dict())	

	# 获取账单
	url = 'http://service.zj.10086.cn/yw/bill/billDetail.do?menuId=13003&bid=BD399F39E69148CFE044001635842132&month=12-2018'
	resp = requests.get(url,headers=service_headers,cookies=bill_cookies,verify=False)
	print(resp.text)	



	#  ========= 爬取语音详单 =======
	print('==========语音详单=====\n\n\n\n')
	# 获取详单表单id
	url = 'http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do?menuId=13009'
	resp = requests.get(url,headers=service_headers,cookies=cookies,verify=False)
	SAMLRequest = re.search(r'name="SAMLRequest" value="([\s\S]+?)"',resp.text).group(1).replace('\n','')
	RelayState = re.search(r'name="RelayState" value="(.+?)"',resp.text).group(1)
	cookies.update(resp.cookies.get_dict())

	# 详单表单id登录
	url = 'https://zj.ac.10086.cn/POST'
	data = {'SAMLRequest':SAMLRequest,'RelayState':RelayState}
	resp = requests.post(url,headers=service_headers,data=data,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())
	SAMLart = re.search(r'name="SAMLart" value="(.+?)"',resp.text).group(1)
	RelayState = re.search(r'name="RelayState" value="(.+?)"',resp.text).group(1)

	# 详单表单重定向
	url = 'http://service.zj.10086.cn/servlet/assertion'
	data = {
	"AppSessionId":"NotExist",
	"SAMLart":SAMLart,
	"isEncodePassword":"2",
	"displayPic":"0",
	"RelayState":RelayState,
	"isEncodeMobile":"2",
	}
	resp = requests.post(url,headers=service_headers,data=data,cookies=cookies,allow_redirects=False,verify=False)
	cookies.update(resp.cookies.get_dict())

	# 发送短信，移动限制30分只能发一次
	url = 'http://service.zj.10086.cn/yw/detail/secondPassCheck.do'
	data = {
	"validateCode":"",
	"bid":"BC5CC0A69BC10482E044001635842132",
	}
	resp = requests.post(url,data=data,headers=service_headers,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())

	# 填写短信
	url = 'http://service.zj.10086.cn/yw/detail/secondPassCheck.do'
	data = {
	"validateCode":input('please input sms code ...'),
	"bid":"BC5CC0A69BC10482E044001635842132",
	}
	resp = requests.post(url,data=data,headers=service_headers,cookies=cookies,verify=False)
	cookies.update(resp.cookies.get_dict())
	if resp.text.find('12') == -1:
		print('bad sms code')
		return False

	# 查询详单	
	url = 'http://service.zj.10086.cn/yw/detail/queryHisDetailBill.do?bid=&menuId=13009&listtype=1&month=01-2019'
	resp = requests.get(url,headers=service_headers,cookies=cookies,verify=False)
	print(resp.text)

	return 'res'


def parse(res):
	"""解析函数"""
	pass


def main():
	cookies = login()
	res = crawl(cookies)
	# print(cookies)




if __name__ == '__main__':
	main()

