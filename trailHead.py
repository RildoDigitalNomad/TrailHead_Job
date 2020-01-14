import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By	
import simple_salesforce
from simple_salesforce import Salesforce
import datetime

def main():
	sf = Salesforce(password='******', username='******', organizationId='******') #SFDC Credential and ORG ID
	bulkSFDCArray = []
	noRead = []
	success = 0
	fail = 0
	initTotal = datetime.datetime.now()
	contacts = sf.query("SELECT Id, Trailhead_Link__c, Firstname, "+
						"Points__c, Badge_Count__c, LastName FROM Contact " +
						"WHERE Trailhead_Link__c != '' "+
						"AND Has_Profile_Private__c = False "+
						"ORDER BY Points__c DESC")
	for contact in contacts['records']:
		initFor = datetime.datetime.now()
		running = True
		browser = webdriver.Chrome()
		browser.get(contact['Trailhead_Link__c'])
		print(">>>>>>>>>>><<<<<<<<<<<<<<<<<<############")
		while running:
			try:
				elements = browser.find_elements(By.XPATH, "//div/div/div[2]/div/div[2]/div/div/div[2]/c-trailhead-rank/c-lwc-card/article/div/slot/div[2]/c-lwc-tally[2]/span/span[1]")	
				badgets = browser.find_elements(By.XPATH, "//div/div/div[2]/div/div[2]/div/div/div[2]/c-trailhead-rank/c-lwc-card/article/div/slot/div[2]/c-lwc-tally[1]/span/span[1]")
				print('Name:: ' + contact['FirstName'] + ' ' + contact['LastName'] + ' -- Points:: -- ' + (elements[0].text.replace('.', '').replace(',', '')) + ' -- Badges:: -- ' + (badgets[0].text.replace('.', '').replace(',', ''))  )
				print(">>>>>>>>>>><<<<<<<<<<<<<<<<<<############")
				newContact = {'Id': contact['Id'], 'Points__c':int((elements[0].text.replace('.', '').replace(',', ''))), 'Badge_Count__c':int((badgets[0].text.replace('.', '').replace(',', '')))}
				#print(elements[0])
				bulkSFDCArray.append(newContact)
				running = False
				browser.quit()
			except Exception as e:
				print("Waiting Web Browser load the profile!")
				if not( browser.title == 'Trailblazer | Profile' ):
					print("Detected: something wrong at the Trailhead profile URL. User: " + contact['FirstName'])
					noReadContact = {'Id': contact['Id'], 'FirstName': contact['FirstName'], 'LastName':contact['LastName']}
					noRead.append(noReadContact)
					running = False
					browser.quit()
				pass
	result = sf.bulk.Contact.update(bulkSFDCArray)
	for bulk in result:
		if (bulk['success'] == True):
			success += 1
		else:
			fail +=1
			
	print("Success:: " + str(success) + " --- AND --- Faill:: " + str(fail) )
	print(">>>>>>>>>>><<<<<<<<<<<<<<<<<<############")
	print("Operation tooks (minutes):: ", datetime.datetime.now() - initTotal)
	print("Had " + str(len(noRead)) + " contacts that could not be read. Following")
	for contactError in noRead:
		print("Name:: " + contactError['FirstName'] + ' ' + contactError['LastName'])

main()