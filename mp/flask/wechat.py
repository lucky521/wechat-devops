# -*- coding: utf-8 -*-
import flask
from flask import request
import hashlib
import xml.etree.cElementTree as ET
import time
import urllib2
import json
import threading

app = flask.Flask(__name__)

selftoken = "12345"
appid = "12345"
appsecret = "12345"
access_token = ""

################################################################

def access_token_timer():
	global access_token
	url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" %(appid, appsecret)
	print url
	res = urllib2.urlopen(url).read()
	print type(res)
	res = json.loads(res)
	access_token = res["access_token"]
	expires = res["expires_in"]
	print(time.ctime())
	thread.Timer(int(expires), access_token_timer).start()


################################################################

@app.route('/')
def index():
	return "hello, flask"

@app.route('/wechat',methods=['GET','POST'])
def wechat():
	if request.method=='GET':
		token=selftoken
		data=request.args
		signature=data.get('signature','')
		timestamp=data.get('timestamp','')
		nonce =data.get('nonce','')
		echostr=data.get('echostr','')

		sig=[timestamp,nonce,token]
		sig.sort()
		sig=''.join(sig)
		if(hashlib.sha1(sig).hexdigest()==signature):
			return flask.make_response(echostr)
		else:
			return "hello wechat"
	else: # post request
		rec=request.stream.read()
		xml_rec=ET.fromstring(rec)
		tou = xml_rec.find('ToUserName').text
		fromu = xml_rec.find('FromUserName').text
		msgtype = xml_rec.find('MsgType').text
		xml_rep = ""
		if msgtype == 'text':
			content = xml_rec.find('Content').text
			#print isinstance(content, unicode)
			print "get message "+ content.encode('utf-8') + " from " + fromu
			xml_rep = "<xml>\
				<ToUserName><![CDATA[%s]]></ToUserName>\
				<FromUserName><![CDATA[%s]]></FromUserName>\
				<CreateTime>%s</CreateTime>\
				<MsgType><![CDATA[text]]></MsgType>\
				<Content><![CDATA[%s]]></Content>\
				</xml>" %(fromu, tou, int(time.time()), "Haha "+ content.encode('utf-8') )
			print xml_rep
		elif msgtype == 'image':
			picurl = xml_rec.find('PicUrl').text
			mediaid = xml_rec.find('MediaId').text
			xml_rep = "<xml>\
				<ToUserName><![CDATA[%s]]></ToUserName>\
				<FromUserName><![CDATA[%s]]></FromUserName>\
				<CreateTime>%s</CreateTime>\
				<MsgType><![CDATA[image]]></MsgType>\
				<Image><MediaId><![CDATA[%s]]></MediaId></Image>\
				</xml>" %(fromu, tou, int(time.time()), mediaid )
			print xml_rep

		return xml_rep


if __name__ == '__main__':
	app.run(host="0.0.0.0",
		port=80)
