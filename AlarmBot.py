import requests
import json
import sys

'''
Usage example:

To initiate: 
    from AlarmBot import alarmBot
    {name} = alarmBot('image' OR 'markdown' OR 'text',{input data})
To Post
    {name}.post()

'''

class alarmBot(object):

    def __init__(self, msgType, input):
        self.webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=fb73088c-f65a-4549-ade0-be1e8134d8b7"
        self.msgType = msgType
        self.data = input

    def post(self):
        headers = {'Content-Type': 'application/json'}
        if self.msgType == 'image':
            res = requests.post(self.webhook, headers=headers, json=self.data)
        elif self.msgType == 'markdown':
            payload = '{"msgtype": "' + self.msgType + '","' + self.msgType + '": { "content": "' + self.data + '"}}'
            res = requests.post(self.webhook, data=payload.encode('utf-8'), headers=headers)
        elif self.msgType == 'text':
            payload = '{"msgtype": "' + self.msgType + '","' + self.msgType + '": { "mentioned_mobile_list":["@all"], "content":"' + self.data + '"}}'
            res = requests.post(self.webhook, data=payload.encode('utf-8'), headers=headers)
        else:
            payload = ''      

        if json.loads(res.text)['errmsg']=='ok':
            #print('success')
            pass
        else:
            print('Bot Send Failed')
            sys.exit()