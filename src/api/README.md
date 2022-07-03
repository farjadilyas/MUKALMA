# MUKALMA API
The Flask Application that uses the Mukalma models to run it on a Flask Web Server. This allows the model to be used for Testing and our Front-End Application. This document details the requests and the response strucuture of the API, using HTTP GET and POST Requests. 

*Follow the Installtion instructions on the main `README` to learn how to install the API*

## Usage

### 1. Reply
Use this request to get a reply to a message from the model.
|||
|---|---|
|Path|`<API_URL>/reply`|
|Type|HTTP POST|
|Request Body| JSON |

**Request Parameters**
|Parameter|Type|Description|
|---|---|---|
|`message`|`String`|Your text message for which we need the reply|
|`async`|`Boolean`|Toggle API request method. **Please use `False` for this when connecting from anything other than Front-End**|
|`m_id`|`Integer`|Message ID. Can be sent as `0`. **Only used by Front-End**|

**Response Structure**
|Key|Value|Description|
|---|---|---|
|`response`|`String`|Response to the message|
|`candidates`|`Array`|Candidate responses from the model|
|`knowledge_sent`|`String`|Knowledge span used for the response|
|`knowledge_source`|`String`|Knowledge source used for the response|
|`topic`|`Object`|Dictionary containing information about the topic used by the model|

### 2. Connect
Use this request to test your connection to the API. 
|||
|---|---|
|Path|`<API_URL>/connect`|
|Type|HTTP GET|


### 3. Clear
Use this request to clear the current context of the model.
|||
|---|---|
|Path|`<API_URL>/connect`|
|Type|HTTP GET| 

## Technologies
<div>
    <img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original.svg" title="Python" **alt="Python" width="40" height="40"/>
    <img src="https://github.com/devicons/devicon/blob/master/icons/flask/flask-original.svg" title="Flask" **alt="Flask" width="40" height="40"/>
</div>

## License
GNU General Public License v3.0

## Contact us
- [Farjad Ilyas](mailto:ilyasfarjad@gmail.com?subject=[GitHub]%20Source%20Han%20Sans)
- [Nabeel Danish](mailto:nabeelben@gmail.com?subject=[GitHub]%20Source%20Han%20Sans)
- [Saad Saqlain](mailto:i180694@nu.edu.pk?subject=[GitHub]%20Source%20Han%20Sans)