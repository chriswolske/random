def loadWeb(filename):
    df = pd.DataFrame()
    f = open(filename)
    for l in f:
        try:
            date, time, site, code, status, elapsed = l.split(' ')
            #print(date,time,code,status,elapsed)
            ts=pd.Timestamp(date+' '+time[:-4]+'.'+time[-3:])
            if site == 'Exception':
                elapsed = 0
                code = 999
                status = 'EXCP'
            sec = float(elapsed[0])*3600+float(elapsed[2:4])*60+float(elapsed[5:-2])
            df=df.append({'timestamp':ts,'site':site,'code':code, 'status':status, 'elapsed':sec},ignore_index=True)
        except:
            pass
    return df.set_index('timestamp')

def calcPercent(data,site,code):
    sitedata=data[data['site'] == site]
    x = len(sitedata[sitedata['code'] == code])
    if x == 0:
        return 0
    else:
        return float(len(sitedata))/x*100
