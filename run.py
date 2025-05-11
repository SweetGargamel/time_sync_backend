from utils import create_app

app = create_app()
app.config['UPLOAD_FOLDER'] = './upload'  # 设置上传目录

if __name__ == '__main__':
    app.run(debug=True,port=5001)
    # app.run(port=5001)