from __future__ import print_function
from flask import Flask, redirect, url_for, request, jsonify, render_template
import json,sys
import sqlite3


app = Flask(__name__)

dataList = []

def getOrgData(orgid):
	orgdict = {}
	#First query orgTable to get orgName
	conn = sqlite3.connect('OrgData.db')
	print("Opened database successfully")
	
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	cur.execute("Select orgName from orgTable where orgID = {}".format(orgid))
	rows1 = cur.fetchall()
	#print(rows1)

	if len(rows1) != 0:
		cur.execute("WITH RECURSIVE teamPathTable(orgID, teamID, teamName, teamPath) AS(\
			SELECT orgID, teamID, teamName, teamName || ';' || repoList || ';' || userids  as teamPath\
			FROM teamTable\
			WHERE parent_team_id IS NULL\
			UNION ALL\
			SELECT tt.orgID, tt.teamID, tt.teamName, tpt.teamPath || ' > ' || tt.teamName || ';' || tt.repoList || ';' || tt.userids\
			FROM teamPathTable AS tpt JOIN teamTable AS tt\
			ON tpt.teamID = tt.parent_team_id\
			)\
			SELECT * FROM teamPathTable\
			WHERE orgID = {} ORDER BY teamID;".format(orgid)
		)

		rows2 = cur.fetchall()
		#print(rows2)

	conn.close()
	print("Closed database successfully")

	if len(rows1) != 0 and len(rows2) != 0:
		#return "exist"
		#create json object here with data from db
		orgdict['orgID'] = orgid			#orgid added
		orgdict['orgName'] = rows1[0]["orgName"]	#orgname added
		#Loop through all elements of rows2
		orgdict['Teams'] = []
		for row in rows2:
			#print(row)	#each row will represent a single team
			teamdict = {}
			teamid = row["teamID"]
			teamReachPath = row["teamPath"]
			#print(teamInfo)
			teamDepths = teamReachPath.split('>')
			#print(teamDepths)
			teamLevel = orgdict['Teams']
			for depth in teamDepths:
				temp = depth.split(';')
				teamName = temp[0]
				repoList = temp[1]
				userids = temp[2]
				#print(temp)
				#check from root till end
				found = False
				for presentTeamDict in teamLevel:
					if presentTeamDict["TeamName"] == teamName:
						if "Teams" not in presentTeamDict:
							presentTeamDict["Teams"] = []
						teamLevel = presentTeamDict["Teams"]
						#print('hi.................')
						found = True
						break
	
				if found == False:	#team not found in present dict, insert an entry
					teamLevel.append({"TeamName" : teamName, "Repos" : repoList, "users" : userids})

		return orgdict

@app.route('/org/<int:orgid>/')
def getOrgStruct(orgid):
	'''
	#Read JSON corresponding to organisation
	with open('./orgSt.json') as jsonData :
		orgStructure = json.load(jsonData)
	orgList = orgStructure["Org"]
	for orgdict in orgList:
		print(orgdict, file = sys.stdout)
		if orgdict["OrgID"] == orgid:
			return jsonify(orgdict)
	'''
	dataDict = getOrgData(orgid)	
	if dataDict:
		return jsonify(dataDict)
	else:
		return 'Invalid Organisation %d... No data exists...' % orgid

def parseJSONData(teamList, userid, orgName):
	for teamDict in teamList:
		#check if a particular user id exists in this team or not
		#print(teamDict["users"])
		userlist = teamDict["users"].split(',')
		#print(userlist)
		if userid in userlist:
			Dict = {}
			if "Repos" in teamDict:
				#print(teamDict["Repos"])
				repos = teamDict["Repos"].split(',')
				Dict["Repos"] = repos
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
	'''
	#ParseJSON data according to userid and return accordingly
	with open('./orgSt.json') as jsonData :
                orgStructure = json.load(jsonData)
        orgList = orgStructure["Org"]
	'''

	conn = sqlite3.connect('OrgData.db')
        print("Opened database successfully")

        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("Select * from orgTable;")
        orgrows = cur.fetchall()
        print(orgrows)

	conn.close()
        print("Closed database successfully")

	for organisation in orgrows:
		orgName = organisation["OrgName"]
		orgid = organisation["orgID"]
		teamList = getOrgData(orgid)["Teams"]
		print(teamList)
		parseJSONData(teamList, userid, orgName)
	#print(dataList)
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
