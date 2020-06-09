import requests


def youdao_translate(text):
    url = 'http://fanyi.youdao.com/translate'
    if type(text) == list:
        src = ','.join(text)
    else:
        src = text
    data = {
        'doctype': 'json',
        # 'type': 'EN2ZH_CN',
        'type': 'ZH_CN2EN',
        'i': src,
    }
    rs = requests.get(url=url, params=data)
    try:
        trans_data = rs.json()['translateResult']
        tgt = [t['tgt'] for t in trans_data[0]]
        return tgt
    except Exception as e:
        # print('There is an error in translation')
        print(e)
        return []

if __name__ == '__main__':
    print(youdao_translate(['网页应用','数据模型']))