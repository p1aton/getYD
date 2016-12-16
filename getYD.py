import json, requests
import sys, datetime
import csv

url4 = 'https://api.direct.yandex.ru/live/v4/json/'
url5 = 'https://api.direct.yandex.ru/json/v5/'
token = ''


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def assignCampaignsNames(x):    
    x['CampaignName'] = list(filter(lambda y: x['CampaignID'] == y['Id'], campigns))[0]['Name']
    return x

def GetCampaignsList():
	CampaignsListData={}
	data = {
		'method': 'get',
		'params': {
			'SelectionCriteria': {},
			'FieldNames': ['Id', 'Name']
		}
	}
	headers = {
		'Authorization': 'Bearer ' + token,
		'Accept-Language': 'ru'
	}
	jdata = json.dumps(data, ensure_ascii=False).encode('utf8')
	response = requests.post(url5 + 'campaigns', data=jdata, headers=headers)
	body = response.json();
	try:
	    CampaignsListData = body['result']['Campaigns']
	except KeyError:
	    raise Exception(body)
	return CampaignsListData

def GetSummaryStat(CampaignIDs, StartDate, EndDate):
	BannersStatData={}
	data = {
		'method': 'GetSummaryStat',
		'token': token,
		'locale': 'ru',
		'param': {
			"CampaignIDS": CampaignIDs,
			"StartDate": StartDate,
			"EndDate": EndDate
		},	
	}		
	jdata = json.dumps(data, ensure_ascii=False).encode('utf8')
	response = requests.post(url4,jdata)
	body = response.json();
	try:
		BannersStatData = body['data']
	except KeyError:
		raise Exception(body)
	return BannersStatData;

todayDate = datetime.date.today()
if todayDate.day > 25:
    todayDate += datetime.timedelta(7)
data1 = todayDate.replace(day=1)
FirstDayMonth = str(data1)

data2 = datetime.date.fromordinal(datetime.date.today().toordinal()-1)
Yesterday = str(data2)

delta = data2 - data1

campigns = GetCampaignsList()
campignsIDs = list(map(lambda x: int(x['Id']), campigns))
campignsIDs = list(chunks(campignsIDs, round(len(campignsIDs) * (delta.days + 1) / 1000)))
allStat = []
for ids in campignsIDs:
	statistics = GetSummaryStat(ids,FirstDayMonth,Yesterday)
	statistics = list(map(assignCampaignsNames, statistics))
	allStat = sum([statistics, allStat], [])

with open('data.csv', 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file,delimiter=";", fieldnames=['StatDate', 'CampaignID', 'CampaignName','ShowsSearch','ShowsContext','ClicksSearch','ClicksContext','SumSearch','SumContext'], dialect='excel')
    csv_writer.writeheader()
    for item in allStat:
        csv_writer.writerow({
        	'StatDate': item['StatDate'],
        	'CampaignID': item['CampaignID'],
        	'CampaignName': item['CampaignName'],
        	'ShowsSearch': item['ShowsSearch'],
        	'ShowsContext': item['ShowsContext'],
        	'ClicksSearch': item['ClicksSearch'],
        	'ClicksContext': item['ClicksContext'],
        	'SumSearch': str(item['SumSearch']).replace('.',','),
        	'SumContext': str(item['SumContext']).replace('.',',')
        	})
