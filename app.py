from flask import Flask, render_template, request, jsonify
import jira_api

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/issue', methods=['POST'])
def issue_search():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    data = jira_api.issue_search(start_date=start_date, end_date=end_date)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
