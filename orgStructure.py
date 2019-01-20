from __future__ import print_function
from flask import Flask, redirect, url_for, request, jsonify, render_template
import json,sys

app = Flask(__name__)

dataList = []

@app.route('/org/<int:orgid>/')
def getOrgStruct(orgid):
	#Read JSON corresponding to organisation
	with open('./orgSt.json') as jsonData :
		orgStructure = json.load(jsonData)
	orgList = orgStructure["Org"]
	for orgdict in orgList:
		print(orgdict, file = sys.stdout)
		if orgdict["OrgID"] == orgid:
			return jsonify(orgdict)

	return 'Invalid Organisation %d... No data exists...' % orgid

def parseJSONData(teamList, userid, orgName):
	for teamDict in teamList:
		#check if a particular user id exists in this team or not
		if userid in teamDict["users"]:
			Dict = {}
			if "Repos" in teamDict:
				#print(teamDict["Repos"])
				Dict["Repos"] = teamDict["Repos"]
			else:
				#print("Empty repo")
				Dict["Repos"] = ''
			#print(teamDict["TeamName"])
			Dict["Team"] = teamDict["TeamName"]
			#print(orgName)
			Dict["Org"] = orgName
			dataList.append(Dict)
		if "Teams" in teamDict:
			parseJSONData(teamDict["Teams"],userid, orgName)

@app.route('/user/<userid>/')
def getUserData(userid):
	#ParseJSON data according to userid and return accordingly
	with open('./orgSt.json') as jsonData :
                orgStructure = json.load(jsonData)
        orgList = orgStructure["Org"]

	for organisation in orgList:
		orgName = organisation["OrgName"]
		parseJSONData(organisation["Teams"], userid, orgName)
	print(dataList)
	if not dataList:
		return "Data corresponding to particular UserId doesn't exist..."
	else :
		return render_template('userData.html', userid = userid, data = dataList)
	

@app.route('/org', methods = ['POST', 'GET'])
def orgRequest():
	if request.method == 'POST':
		orgid = request.form['orgid']
		print(orgid, file = sys.stdout)
		if orgid != '':
			return redirect(url_for('getOrgStruct', orgid = orgid))
		else:
			return "Please enter an organisation id"

@app.route('/user', methods = ['POST', 'GET'])
def dataRequest():
	if request.method == 'POST':
		dataList[:] = []
		userid = request.form['userid']
		print(userid, file = sys.stdout)
		if userid != '':
			return redirect(url_for('getUserData', userid = userid))
		else:
			return "Please enter a user name"

if __name__ == '__main__':
	#app.debug = True
	#app.run()
	app.run(debug = True)
