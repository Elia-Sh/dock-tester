# import the Flask class from the flask module
from flask import Flask, request
from flask_caching import Cache

INTERNAL_PORT = 5000

# create the application object
app = Flask(__name__)

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",    # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)
LATEST_REQUEST_KEY = 'latest_response_str'

# use decorators to link the function to a url
# @app.route('/')
# def home():
#     # note that / route is not open
#     return "Hello, World!"  # return a string

@app.route('/reverse', methods=['GET'])
def reverse():
    '''
    test via shell:
        curl -X GET -G \
            'http://localhost:5000/reverse' \
        -d in=Through%20deal%20style%20mention%20dream%20store,%20training%20at%20others%20billion%20teacher%20process.
        
    same as: 
        curl 'http://localhost:5000/reverse?in=Through%20deal%20style%20mention%20dream%20store,%20training%20at%20others%20billion%20teacher%20process.'

    '''
    ARGEUMENT_NAME = 'in'
    words_str = request.args.get(ARGEUMENT_NAME, default="", type=str)  # already addresses special chars like %20 aka space
    chars_list = list(words_str)
    reverse_words(chars_list)
    str_result = ' '.join(chars_list)
    cache.set(LATEST_REQUEST_KEY, value = str_result)   # storing as lastest reuqest
    response_json = {
        'result': str_result
    }
    return response_json  # flask converts dict to JSON

@app.route('/restore', methods=['GET'])
def restore():
    '''
    API 2: `/restore`  
    The API will return the last result from API "/reverse"
    '''
    last_reverse_request = cache.get(LATEST_REQUEST_KEY)
    if last_reverse_request:
        # not persistant restore API -> if no prev requests will return ''
        last_reverse_request = ''
    response_json = {
        'result': last_reverse_request
    }
    return response_json

def reverse_list_inline(a_list = [], start=None, end=None):
    """
    O(1) space
    O(n)
    * len(alist) > j > i
    """
    if not start:
        start = 0
    if not end:
        end = len(a_list) -1
    while(start<end):
        temp = a_list[start]
        a_list[start] = a_list[end] #Swaping
        a_list[end]=temp
        start+=1
        end-=1
    #a_list reversed

def reverse_words(a_list = []):
    """
    O(1) space
    O(n)

    1. reverse whole string, 
    2. reverse each word
        2.1 for each char -
        2.2     if space
        2.3         -> end of prev word -> start of new word
        2.4         find next space -> or end of string
    3. reverse string again -> to reverse inial "reversing"
    """
    reverse_list_inline(a_list)
    list_len = len(a_list)
    left_space_index = 0
    right_space_index = 0
    i = 0   # 
    while i < list_len:
        if a_list[i].isspace():
            # print(f'found space at: {i}')
            reverse_list_inline(a_list, left_space_index, i -1) # -1 to leave space in it's place 
            left_space_index = i +1
            # print(f'---> after reverse of substing: {a_list}')
        i+=1
    reverse_list_inline(a_list, left_space_index, list_len -1)
    #a_list reversed

# start the server with the 'run()' method
# exposing connection to outside world with host="0.0.0.0"
if __name__ == '__main__':
    app.run(debug=True, 
    port=INTERNAL_PORT, host="0.0.0.0")
