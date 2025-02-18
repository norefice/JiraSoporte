from flask import Flask, render_template, request, jsonify
import jira_api
import config

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

@app.route('/issues_by_org')
def issues_by_org():
    org_name = request.args.get('org_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    issues = jira_api.get_issues_by_org(org_name, start_date=start_date, end_date=end_date)
    return render_template('issues_by_org.html', org_name=org_name, issues=issues, config=config)

if __name__ == '__main__':
    app.run(debug=True)
