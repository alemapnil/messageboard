import os, boto3, traceback,uuid
import mysql.connector.pooling
from flask import *
from dotenv import load_dotenv


load_dotenv()


dbconfig = {
"host":'dbfromaws.ckbctsif2sjr.us-east-1.rds.amazonaws.com',
"port":'3306',
"database":'message_db',
"user": os.getenv('RDS_USER'),
"password": os.getenv('RDS_PASSWORD'),
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool", pool_size = 5, **dbconfig) #create a pool which connect with DB



app = Flask (__name__) 
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False
app.secret_key = os.urandom(24)

ALLOWED_EXTENSIONS = {'png','jpg', 'jpeg', 'gif','tif'}


s3 = boto3.client('s3', aws_access_key_id = os.getenv('AWS_ACCESS_KEY'),
                      aws_secret_access_key = os.getenv('AWS_SECRET_KEY'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(msg,img_url):
	global data
	try:
		CN1 = pool.get_connection() #get a connection with pool.  
		print(CN1.connection_id,'RDS ID create')   
		cursor = CN1.cursor()

		insert = """ insert into `message` (`word`, `img`) values(%s,%s);"""
		cursor.execute(insert, (msg , img_url))
	except Exception as e:
		data = {"error": True,"message": "資料庫內部錯誤"}
		print('資料庫內部錯誤',type(e),e)
		CN1.rollback()
	else:
		data = {"ok": True, 'msg' : msg, 'img_url': img_url}
		print('upload_file commit')
		CN1.commit()

	finally:
		print(CN1.connection_id, 'upload_file close...', CN1.is_connected())
		cursor.close()
		CN1.close()



def get_file():
	global data
	try:
		CN1 = pool.get_connection() #get a connection with pool.  
		print(CN1.connection_id,'RDS ID create')  
		cursor = CN1.cursor()

		sql = """SELECT * FROM `message`
			order by `id` desc 
		"""
		cursor.execute(sql)

		allList = cursor.fetchall() #tuple or None
		data = {'ok' : True, 'allfiles': allList}

	except Exception as e:
		data = {"error": True,"message": "資料庫內部錯誤"}
		print('資料庫內部錯誤',type(e),e)
		CN1.rollback()

	finally:
		print(CN1.connection_id, 'get_file close...', CN1.is_connected())
		cursor.close()
		CN1.close()


# Pages
@app.route("/")
def index():
	return render_template("index.html")


@app.route('/send', methods = ['POST'])
def send():
	global data

	#測試上傳檔案正確與否
	try:
		message = request.form['message']
		picture = request.files['picture']
	except :
		print(traceback.format_exc(message))
		data = {"error": True,"message": "輸入的檔案錯誤"}
		return jsonify(data)

	#附檔名是否合格
	if allowed_file(picture.filename):
		s3_object = 'message_img/' + uuid.uuid1().hex +'.' + picture.filename.rsplit('.', 1)[1].lower()
		cdn_url = 'https://d3i2i3wop7mzlm.cloudfront.net/' + s3_object
		try:
			s3.upload_fileobj(picture, 'bucketfromaws', s3_object)	
			upload_file(message, cdn_url)
		except: 
			print(traceback.format_exc())
			data = {"error": True,"message": "伺服器內部錯誤"}
		return jsonify(data)

	else:
		data = {"error": True,"message": "非圖片檔"}
		return jsonify(data)


@app.route('/send', methods = ['GET'])
def getall():
	global data
	get_file()
	return jsonify(data)



app.run(host='0.0.0.0')