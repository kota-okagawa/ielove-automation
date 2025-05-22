from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ 自動実行APIが稼働中です'

@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = subprocess.run(['python3', 'ielove_scraper.py'], capture_output=True, text=True)
        return f"✅ 実行完了\n\n{result.stdout}", 200
    except Exception as e:
        return f"❌ 実行エラー: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
