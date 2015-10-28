from flask import Flask
import requests
import logging

app = Flask(__name__)
logging.basicConfig(filename='web_svr.log', level=logging.WARNING, format='%(asctime)s %(message)s')

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/check/<site>')
def check(site):
    #print(site)
    try:
        r = requests.get(site,timeout=5.0)
    except requests.exceptions.ConnectionError:
        logging.warning('%s %s ConnectError' % (site, r.status_code))
        return ('<strong>%s</strong>: Connection Error' % (site, r.status_code))
    except requests.exceptions.ConnectTimeout:
        logging.warning('%s %s ConnectTimeout' % (site,r.status_code))
        return ('<strong>%s</strong>: Connection Timeout' % site)

    if r.status_code == 200:
        logging.warning('%s %s OK %s' % (site, r.status_code, r.elapsed))
        return ('<strong>%s</strong> is UP; Status = %i; ResponseTime: %s' % (site, r.status_code, r.elapsed))
    else:
        logging.warning('%s %s CHECK %s' % (site, r.status_code, r.elapsed))
        return ('%s CHECK status = %i; ResponseTime: %s' % (site, r.status_code, r.elapsed))


@app.route('/checktest')
def checktest():
    sites = ['https://www.eginniemae.net','http://www.ginniemae.gov','www.nostie.non','httpbin.org/delay/1']
    output=[]
    for s in sites:
        output.append(check(s))
    return str(output)
        
@app.route('/checkgnma')
def checkgnma():
    sites = ['https://www.eginniemae.net','https://uat.eginniemae.net',
        'https://sit.eginniemae.net','http://www.ginniemae.gov', 'https://bulk.ginniemae.gov',
        'https://ccprod.ginniemae.gov/check','http://cms.ginniemae.gov','https://cms.ginniemae.gov','http://fr.ginniemae.gov/fr/login.asp', 'http://fms.ginniemae.gov/loadbalance.htm']
    output=''
    for s in sites:
        output = output +check(s)+ '<p>'
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=False)

