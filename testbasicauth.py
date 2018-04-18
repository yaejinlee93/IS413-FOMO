import requests

response = requests.get('http://localhost:8000/catalog/search.find/', auth=('test@test.com', 'asdfasdf1'), params={
    'page':1,
    'name':'a',
    'category':'Instruments',
    'max_price':500.00,
})

print('Status code', response.status_code)
print(response.json())
