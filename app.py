from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import jira_api
import config

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

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

@app.route('/issue/<issue_key>')
def issue_detail(issue_key):
    issue = jira_api.get_issue_details(issue_key)
    if issue:
        return render_template('issue_detail.html', issue=issue)
    flash('Issue not found', 'error')
    return redirect(url_for('index'))

@app.route('/issue/<issue_key>/comment', methods=['POST'])
def add_comment(issue_key):
    body = request.form.get('body')
    comment_type = request.form.get('comment_type', 'internal')
    files = request.files.getlist('attachments')
    
    if jira_api.add_comment(issue_key, body, comment_type, files):
        flash('Comment added successfully', 'success')
    else:
        flash('Failed to add comment', 'error')
    
    return redirect(url_for('issue_detail', issue_key=issue_key))

@app.route('/issue/<issue_key>/status', methods=['POST'])
def change_status(issue_key):
    new_status = request.form.get('new_status')
    
    if jira_api.change_status(issue_key, new_status):
        flash('Status updated successfully', 'success')
    else:
        flash('Failed to update status', 'error')
    
    return redirect(url_for('issue_detail', issue_key=issue_key))

if __name__ == '__main__':
    app.run(debug=True)
