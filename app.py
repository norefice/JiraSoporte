from flask import Flask, render_template
import metrics
import jira_api

app = Flask(__name__)

@app.route('/')
def index():
    data = metrics.calculate_metrics()
    return render_template('index.html', data=data)

@app.route('/issue')
def issue_search():
    data = jira_api.issue_search()
    return render_template('index.html', data=data)    

if __name__ == '__main__':
    app.run(debug=True)
