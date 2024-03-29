import cgi
import os
import random
import datetime
import urllib


from xml.dom.minidom import Document
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import webapp

from Models import * 
from FirstPage import FirstPage
from xml.etree.ElementTree import Element, SubElement, tostring, XML, fromstring
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from xml.parsers import expat
from xml.dom.minidom import parseString
import urllib2
import xml.dom.minidom
import re
  

#===============================================================================
# is_present : to check if the category is already present
#===============================================================================
def is_present(self, user_name, category_name):
    categories = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", category_name, user_name)

    for category in categories:
        if category.categoryName.upper() == category_name.upper():
            return True

    return False

#===============================================================================
#  Utility function to include item into the category
#===============================================================================

def createNewItem(item_name, category_name, user_name):
    item_new = AllItems(categoryName=category_name,author=user_name,itemName=item_name)
    item_new.itemName = item_name
    item_new.put()
    
#===============================================================================
#  Utility function to delete item from category
#===============================================================================
    
def delete_item(item_name, category_name, user_name):
      deleteFromAllItems = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2 AND itemName = :3", 
                             category_name, user_name, item_name)
      results = deleteFromAllItems.fetch(100)
      db.delete(results)
      
      deleteFromAllComments = db.GqlQuery("SELECT * FROM AllComments WHERE categoryName = :1 AND itemName = :2", 
                               category_name, item_name)
      results = deleteFromAllComments.fetch(100)
      db.delete(results)
      
      deleteFromAllWinners =  db.GqlQuery("SELECT * FROM AllVotes WHERE categoryName = :1 AND winner = :2", 
                                category_name, item_name)
      results = deleteFromAllWinners.fetch(100)
      db.delete(results)
          
      deleteFromAllLosers =  db.GqlQuery("SELECT * FROM AllVotes WHERE categoryName = :1 AND loser = :2", 
                               category_name, item_name)
      results = deleteFromAllLosers.fetch(100)
      db.delete(results)
      
#===============================================================================
# Class for login functionality
#===============================================================================
    
class Login(webapp.RequestHandler):
  def get(self):
    
    q6 = db.GqlQuery("SELECT * FROM Loggeduser")
    results6 = q6.fetch(100)
    db.delete(results6)  
    
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'  
      template_values = {
          'loggedInUser': users.get_current_user(),
          'url': url,
          'url_linktext': url_linktext 
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/Proceed.html')
      self.response.out.write(template.render(path, template_values))
      
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
   
      template_values = {
        'url': url,
        'url_linktext': url_linktext
      }
    
      path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# Class to initial page after login (to get into the application)
#===============================================================================
class Welcome(webapp.RequestHandler):
  def post(self):
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
      
      q6 = db.GqlQuery("SELECT * FROM Loggeduser")
      results6 = q6.fetch(100)
      db.delete(results6)
      
      loggeduser = Loggeduser()
      loggeduser.loggedInUser = loggedInUser
      loggeduser.logout = logout
      loggeduser.put()
      
      template_values = {
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/welcome.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# To get the screen back to home page
#===============================================================================
class WelcomeBack(webapp.RequestHandler):
  def get(self):
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
          
      loggedInUser = ""
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      
      template_values = {
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/welcome.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# Utility class to create category
#===============================================================================
class CreateCategory(webapp.RequestHandler):
  def get(self):
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
          
      loggedInUser = ""
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      
      template_values = {
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/CreateCategory.html')
      self.response.out.write(template.render(path, template_values))
      
#===============================================================================
# Utility class to add items into the category
#===============================================================================
class AddItems(webapp.RequestHandler):
  def get(self):
        loggedInUser = ""
        loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
        for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
        categsForUser = db.GqlQuery("SELECT * FROM AllCategories where author = :1", loggedInUser)
         
        template_values = {
            'categsForUser': categsForUser,
            'loggedInUser' : loggedInUser,
            'logout': logout
         }

        path = os.path.join(os.path.dirname(__file__), 'templates/UserCategs.html')
        self.response.out.write(template.render(path, template_values))

#===============================================================================
# Utility class to search item into the category
#===============================================================================
class SearchItem(webapp.RequestHandler):
  def get(self):
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
          
      loggedInUser = ""
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      
      template_values = {
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/SearchItem.html')
      self.response.out.write(template.render(path, template_values))
      
      
 #==============================================================================
 # Utility class to export category (initial page)
 #==============================================================================
class ExportIntialXML(webapp.RequestHandler):
  def get(self):
    q4 = db.GqlQuery("SELECT * FROM AllResults")
    results4 = q4.fetch(1000)
    db.delete(results4)
      
    loggedInUser = ""
    loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
    for user in loggeduser:
      loggedInUser = user.loggedInUser
      logout = user.logout
    allCategories = db.GqlQuery("SELECT * FROM AllCategories")
    template_values = {
     'allCategories': allCategories,
     'opt5': "Y",
     'loggedInUser' : loggedInUser,
     'logout': logout
     }
    
    path = os.path.join(os.path.dirname(__file__), 'templates/ExportCatPage.html')
    self.response.out.write(template.render(path, template_values))
    

#===============================================================================
# Utility class to Import XML 
#===============================================================================
class ImportXML(webapp.RequestHandler):  #Export XML For a given Category
  def post(self):
        q4 = db.GqlQuery("SELECT * FROM AllResults")
        results4 = q4.fetch(1000)
        db.delete(results4)
              
        loggedInUser = ""
        loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
        for user in loggeduser:
              loggedInUser = user.loggedInUser
              logout = user.logout
          
        template_values = {
            'loggedInUser': loggedInUser,
            'logout': logout
        }
        user_name = self.request.get('loggedInUser')
        x = self.request.POST.multi['imported_file'].file.read()

        dom = xml.dom.minidom.parseString(x)

        root = fromstring(x)                        
        categoryName = root.findall('NAME')
        
        categoryName = categoryName[0].text
        if is_present(self, user_name, categoryName) == False:
            category_new = AllCategories(categoryName=categoryName,author=user_name)
            category_new.author = user_name
            category_new.categoryName = categoryName
            category_new.expirydate=category_new.date+datetime.timedelta(days=31, hours=20)
            category_new.put()

            # add items in the newly created category
            for child in root:
                if child.tag == "ITEM":
                    childName = child.findall('NAME')
                    createNewItem(item_name=childName[0].text, category_name=category_new.categoryName, user_name=category_new.author)
        
        else:
            self.response.out.write('Category already present(advanced feature).')
            xmlItemList = []
            for child in root:
                if child.tag == "ITEM":
                    childName = child.findall('NAME')
                    xmlItemList.append(childName[0].text)
             
            dbItemList = []
            itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", categoryName, loggedInUser)
            for item in itemsForUser:
                dbItemList.append(item.itemName)
                
            is_dbItem_present = "F"    
            for dbItem in dbItemList:
                is_dbItem_present = "F"
                for xmlItem in xmlItemList:    
                    if dbItem == xmlItem:
                        is_dbItem_present = "T"
                        break
                
                if is_dbItem_present == "F":
                    delete_item(item_name=dbItem, category_name=categoryName, user_name=loggedInUser)
            
            is_xmlItem_present = "F"
            for xmlItem in xmlItemList:
                is_xmlItem_present = "F"
                for dbItem in dbItemList:
                    if xmlItem == dbItem:
                        is_xmlItem_present = "T"
                        break
                
                if is_xmlItem_present == "F":
                    createNewItem(item_name=xmlItem, category_name=categoryName, user_name=loggedInUser)
                        
                    
                                 
        template_values = {
          'loggedInUser':loggedInUser,
          'logout': logout,
          'import_success': "Y"                 
        }                                                              
               
        
        path = os.path.join(os.path.dirname(__file__), 'templates/ImportXML.html')
        self.response.out.write(template.render(path,template_values))
        
#===============================================================================
# Utility class to import XML (intial page)
#===============================================================================
class ImportXMLIntial(webapp.RequestHandler):
  def get(self):
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
          
      loggedInUser = ""
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      
      template_values = {
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/ImportXML.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# Utility call to show valid categories for voting
#===============================================================================
class Voting(webapp.RequestHandler):
  def get(self):
      q4 = db.GqlQuery("SELECT * FROM AllResults")
      results4 = q4.fetch(1000)
      db.delete(results4)
          
      loggedInUser = ""
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      allCategories= AllCategories.all().filter("expirydate >", datetime.datetime.now());
      template_values = {
            'allCategories': allCategories,
            'loggedInUser': loggedInUser,
            'logout': logout,
          }

      path = os.path.join(os.path.dirname(__file__), 'templates/AllCategs.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# Utility class to show the result page
#===============================================================================
class Results(webapp.RequestHandler):
  def get(self):
    q4 = db.GqlQuery("SELECT * FROM AllResults")
    results4 = q4.fetch(1000)
    db.delete(results4)
          
    loggedInUser = ""
    loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
    for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
    allCategories = db.GqlQuery("SELECT * FROM AllCategories")
    template_values = {
                'allCategories': allCategories,
                'opt4': "Y",
                'loggedInUser' : loggedInUser,
                'logout': logout
              }
    
    path = os.path.join(os.path.dirname(__file__), 'templates/AllCategs.html')
    self.response.out.write(template.render(path, template_values))
    
#===============================================================================
# Utility class to show search Intial page
#===============================================================================
class SearchIntialPage(webapp.RequestHandler):
  def get(self):
          q4 = db.GqlQuery("SELECT * FROM AllResults")
          results4 = q4.fetch(1000)
          db.delete(results4)
          
          loggedInUser = ""
          loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
          for user in loggeduser:
              loggedInUser = user.loggedInUser
              logout = user.logout
          searchElement = self.request.get('searchElement')
          resultListFound = []
          count = 0
          allItems = db.GqlQuery("SELECT * FROM AllItems")
          for eachItem in allItems:
              resultStr = ""
              if searchElement in eachItem.itemName:
                 resultStr = eachItem.itemName+"   found in "+eachItem.categoryName
                 resultListFound.append(resultStr)
                 count += 1
              else:
                  if searchElement in eachItem.categoryName:
                      resultStr = eachItem.itemName+"   found in "+eachItem.categoryName
                      resultListFound.append(resultStr)
                      count += 1

           
          
          template_values = {
             'loggedInUser' : loggedInUser,
             'resultListFound' : resultListFound,
             'searchElement': searchElement,
             'count': count,
             'logout': logout
          }

          path = os.path.join(os.path.dirname(__file__), 'templates/SearchPage.html')
          self.response.out.write(template.render(path, template_values))       
  
          
#===============================================================================
# Utility class to pick random item from category 
#===============================================================================
class RandomItems(webapp.RequestHandler):
  def post(self):
      
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      catAndUser = self.request.get('catName')
      x = catAndUser.split(',')
      selectedCat = x[0].strip()
      username = x[1].strip()
      
               
                                  
      itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", selectedCat, username)
      
      count = itemsForUser.count()
      error_msg = ""
      if count < 2:
          error_msg = "Y"
          allCategories= AllCategories.all().filter("expirydate >", datetime.datetime.now());
          template_values = {
            'allCategories': allCategories,
            'loggedInUser': loggedInUser,
            'error_msg': error_msg,
            'logout': logout
          }

          path = os.path.join(os.path.dirname(__file__), 'templates/AllCategs.html')
          self.response.out.write(template.render(path, template_values))
          
      else:    
          if count == 2:
              i = 0
              j = 1
          else:        
              i = random.randint(0, count-1)
              j = random.randint(0, count-1)
              while i == j:
                  i = random.randint(0, count-1)
                  j = random.randint(0, count-1)
          
          itemCount = 0
           
          item1 = ""
          item2 = "" 
             
          for itemInfo in itemsForUser:
              if itemCount == i:
                  item1 = itemInfo.itemName
                  
                  
              if itemCount == j:
                  item2 = itemInfo.itemName
                  
              itemCount+= 1    
                     
          allComments = db.GqlQuery("SELECT * FROM AllComments WHERE categoryName = :1 AND loggedInUser = :2 "+
                                    " AND itemName IN (:3, :4) ", selectedCat, loggedInUser, item1, item2)
          
          previousComment1 = ""
          previousComment2 = ""
          for comments in allComments:
              if comments.itemName == item1:
                 previousComment1 = comments.itemComment
              if comments.itemName == item2:
                  previousComment2 = comments.itemComment
          
          

               
          
          template_values = {
            'item1': item1,
            'item2': item2,
            'previousComment1': previousComment1,
            'previousComment2': previousComment2,
            'loggedInUser': loggedInUser,
            'selectedCat': selectedCat,
            'author': username,
            'logout': logout
            
          }
    
          path = os.path.join(os.path.dirname(__file__), 'templates/VotePage.html')
          self.response.out.write(template.render(path, template_values))  

#===============================================================================
# Utility class to add votes to items to category
#===============================================================================
class NewAddedVote(webapp.RequestHandler):  
  def post(self):
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      selectedCat = self.request.get('selectedCat')
      selectedItem = self.request.get('selectedItem')
      username = self.request.get('username')
      previousitem1 = self.request.get('item1')
      previousitem2 = self.request.get('item2')
      previousComment1 = self.request.get('previousComment1')
      previousComment2 = self.request.get('previousComment2')
      appendComment1 = self.request.get('appendComment1')
      appendComment2 = self.request.get('appendComment2')
      btnClicked = self.request.get('btn')
      
      vote_cast = ""
      if btnClicked != "skip":
          newVote = AllVotes()
          newVote.categoryName = self.request.get('selectedCat')
          newVote.author = self.request.get('username')
          if selectedItem == previousitem1:
              vote_cast = "Y"
              newVote.winner = selectedItem
              newVote.loser = previousitem2
              newVote.put()
          elif selectedItem == previousitem2:
              vote_cast = "Y"
              newVote.winner = selectedItem
              newVote.loser = previousitem1
              newVote.put()
          else:
              
              selectedItem = ""         
      
      if previousComment1 != None: 
          if previousComment1 != "":
              if appendComment1 == "T": 
                  newComment = AllComments()
                  newComment.loggedInUser = loggedInUser
                  newComment.categoryName = selectedCat
                  newComment.itemName = previousitem1
                  newComment.itemComment = previousComment1
                  newComment.put()
          
      if previousComment2 != None:
          if previousComment2 != "":
              if appendComment2 == "T":
                  newComment = AllComments()
                  newComment.loggedInUser = loggedInUser
                  newComment.categoryName = selectedCat
                  newComment.itemName = previousitem2
                  newComment.itemComment = previousComment2
                  newComment.put()
              
      itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", selectedCat, username)
      count = itemsForUser.count()
      error_msg = ""
      if count == 2:
          i = 0
          j = 1
      else:        
          i = random.randint(0, count-1)
          j = random.randint(0, count-1)
          while i == j:
              i = random.randint(0, count-1)
              j = random.randint(0, count-1)
      
      itemCount = 0
       
      item1 = ""
      item2 = ""    
      for itemInfo in itemsForUser:
          if itemCount == i:
              item1 = itemInfo.itemName
          if itemCount == j:
              item2 = itemInfo.itemName
          itemCount+= 1    
      
      allComments = db.GqlQuery("SELECT * FROM AllComments WHERE categoryName = :1 AND loggedInUser = :2 "+
                                " AND itemName IN (:3, :4) ", selectedCat, loggedInUser, item1, item2)
      
      newComment1 = ""
      newComment2 = ""
      for comments in allComments:
          if comments.itemName == item1:
             newComment1 = comments.itemComment
          if comments.itemName == item2:
              newComment2 = comments.itemComment
                         
      template_values = {
        'vote_cast': vote_cast,
        'loggedInUser': loggedInUser,
        'selectedItem': selectedItem,
        'item1': item1,
        'item2': item2,
        'previousComment1': newComment1,
        'previousComment2': newComment2,
        'selectedCat': selectedCat,
        'author': username,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/VotePage.html')
      self.response.out.write(template.render(path, template_values))     
      
#===============================================================================
# Utility class to show the result page
#===============================================================================
class ResultsPage(webapp.RequestHandler):  
  def post(self):
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      catAndUser = self.request.get('catName')
      x = catAndUser.split(',')
      categoryName = x[0].strip()
      username = x[1].strip()

      itemsofCateg = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", categoryName, username)
      votesofCateg = db.GqlQuery("SELECT * FROM AllVotes WHERE categoryName = :1 AND author = :2", categoryName, username)
      
      for itemCat in itemsofCateg:
          item = itemCat.itemName
          userList = []
          userComment = []
          allComments = db.GqlQuery("SELECT * FROM AllComments WHERE categoryName = :1 AND itemName = :2", categoryName, item)
          for comment in allComments:
              userList.append(comment.loggedInUser)
              userComment.append(comment.itemComment)
              
          winCount = 0
          lossCount = 0
          percent = 0
          for voteCat in votesofCateg:
              winner = voteCat.winner
              loser = voteCat.loser
              if item == winner:
                  winCount+= 1
              if item == loser:
                  lossCount+= 1
                      
          if winCount == 0 and lossCount == 0:
              percent = 0
          else:
              sum = winCount + lossCount
              div = float(winCount)/sum
              percent = div * 100
                  
          newResult = AllResults()
          newResult.categoryName = categoryName
          newResult.author = username
          newResult.itemName = item
          newResult.winCount = winCount
          newResult.lossCount = lossCount
          newResult.percentWin = int(percent)
          newResult.userList = userList
          newResult.userComment = userComment
          newResult.put()
                      
      allResults = db.GqlQuery("SELECT * FROM AllResults WHERE categoryName = :1 AND author = :2 ORDER BY percentWin DESC ", categoryName, username)
      
      template_values = {
        'loggedInUser': loggedInUser,                 
        'allResults': allResults,
        'categoryName': categoryName,
        'author': username,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/ResultsPage.html')
      self.response.out.write(template.render(path, template_values))
      
#===============================================================================
# Utility class to add items to category
#===============================================================================
class NewAddedItem(webapp.RequestHandler):  
  def post(self):

      selectedCat = self.request.get('catName')
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      itemName = self.request.get('itemName')
      deletedItems = self.request.get_all('deletedItems')
      
      optionpic = self.request.get('itemImage');
      
      if deletedItems:
          for item in deletedItems:
              deleteFromAllItems = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2 AND itemName = :3", 
                                     selectedCat, loggedInUser, item)
              results = deleteFromAllItems.fetch(100)
              db.delete(results)
          
          for item in deletedItems:
              deleteFromAllComments = db.GqlQuery("SELECT * FROM AllComments WHERE categoryName = :1 AND itemName = :2", 
                                     selectedCat, item)
              results = deleteFromAllComments.fetch(100)
              db.delete(results)
          
          for item in deletedItems:
              deleteFromAllWinners =  db.GqlQuery("SELECT * FROM AllVotes WHERE categoryName = :1 AND winner = :2", 
                                     selectedCat, item)
              results = deleteFromAllWinners.fetch(100)
              db.delete(results)
              
          for item in deletedItems:
              deleteFromAllLosers =  db.GqlQuery("SELECT * FROM AllVotes WHERE categoryName = :1 AND loser = :2", 
                                     selectedCat, item)
              results = deleteFromAllLosers.fetch(100)
              db.delete(results)   
      
      if itemName:       
          itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", 
                                     selectedCat, loggedInUser)
          
          isItemPresent = "F"
          for itemInfo in itemsForUser:
             if itemName == itemInfo.itemName:
                isItemPresent = "T"
                break
                   
          if isItemPresent == "F":     
              newItem = AllItems()
              newItem.categoryName = selectedCat
              newItem.author = loggedInUser
              newItem.itemName = itemName
              newItem.put()
              
          

      itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", 
                                 selectedCat, loggedInUser)
      
      template_values = {
        'itemsForUser': itemsForUser,
        'selectedCat': selectedCat,
        'loggedInUser': loggedInUser,
        'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/UserItems.html')
      self.response.out.write(template.render(path, template_values))

#===============================================================================
# Utility class to upload files to GAP
#===============================================================================
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')  
    blob_info = upload_files[0]
    self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)
    
#===============================================================================
# Utility function to export XML of category
#===============================================================================
class ExportXML(webapp.RequestHandler):  
  def post(self):
        loggedInUser = self.request.get('loggedInUser')
        catAndUser = self.request.get('catName')
        x = catAndUser.split(',')
        selectedCat = x[0].strip()
        username = x[1].strip()
        username = self.request.get('username')
      
        itemsofCateg = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 ", selectedCat)
        
        self.response.headers['Content-Type'] = 'text/xml'
        
        file_name = selectedCat.replace(' ', '_').replace(',','').replace('@','').replace('.','')
        self.response.headers['Content-Disposition'] = "attachment; filename="+str(file_name)+ ".xml"
        root = Element('CATEGORY')
        categoryName = SubElement(root, 'NAME')
        categoryName.text = selectedCat
        for item in itemsofCateg:
            itemTag = SubElement(root, 'ITEM')
            itemNameTag = SubElement(itemTag, 'NAME')
            itemNameTag.text = item.itemName
        self.response.out.write(tostring(root))
        
#===============================================================================
# Utility class to create category( show initial page)
#===============================================================================
class CreateCategoryIntial(webapp.RequestHandler):  
  def post(self):
      loggeduser = db.GqlQuery("SELECT * FROM Loggeduser")
      for user in loggeduser:
          loggedInUser = user.loggedInUser
          logout = user.logout
      loggedInUser = self.request.get('loggedInUser')
      categoryName = self.request.get('catName')
      allCategories = db.GqlQuery("SELECT * FROM AllCategories where author = :1", loggedInUser)
      isCatPresent = "F"
      returnStatus = "Y"
      for categ in allCategories:
          if categoryName == categ.categoryName:
               isCatPresent = "T"
               returnStatus = ""
               break
           
      if isCatPresent == "F":     
          category = AllCategories()
          category.author = loggedInUser
          category.categoryName = categoryName
          category.put()
          
      
      template_values = {
         'categoryAdded' : returnStatus,
         'loggedInUser' : loggedInUser,
         'logout': logout
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/CreateCategory.html')
      self.response.out.write(template.render(path, template_values))
      
#===============================================================================
# Utility class to show all items of the category
#===============================================================================
class AllItemsForUser(webapp.RequestHandler):  
  def post(self):
      selectedCat = self.request.get('catName')
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')
      itemsForUser = db.GqlQuery("SELECT * FROM AllItems WHERE categoryName = :1 AND author = :2", selectedCat, loggedInUser)
      expTimeHH = self.request.get('expTimeHH')
      expTimeMM = self.request.get('expTimeMM')
      expTimeSS = self.request.get('expTimeSS')
      
      currentsurvey = db.GqlQuery("SELECT * "
                                "FROM AllCategories "
                                 "WHERE categoryName=:1 AND  author = :2", selectedCat,loggedInUser)
                #year=int(cgi.escape(self.request.get('year')))
                #month=int(cgi.escape(self.request.get('month')))
      day1=int(cgi.escape(self.request.get('day')))
      hours1=int(cgi.escape(self.request.get('hours')))
      for cntr6 in currentsurvey:
          cntr6.expirydate=cntr6.date+datetime.timedelta(days=day1, hours=hours1)
          cntr6.put()
 
      
      allExpTime = db.GqlQuery("SELECT * FROM ExpirationTime WHERE categoryName = :1 AND loggedInUser = :2", 
                                 selectedCat, loggedInUser)
      template_values = {
        'itemsForUser': itemsForUser,
        'selectedCat': selectedCat,
        'loggedInUser': loggedInUser,
        'logout': logout,
      }

      path = os.path.join(os.path.dirname(__file__), 'templates/UserItems.html')
      self.response.out.write(template.render(path, template_values))
 

   

              
#===============================================================================
# Main mapping
#===============================================================================
application = webapp.WSGIApplication(
                                     [('/', Login),
                                      ('/welcome', Welcome),
                                      ('/welcomeBack', WelcomeBack),
                                      ('/randomItems', RandomItems),
                                      ('/allItemsForUser', AllItemsForUser),
                                      ('/initChoice', FirstPage),
                                      ('/newAddedItem', NewAddedItem),
                                      ('/newAddedVote', NewAddedVote),
                                      ('/resultsPage', ResultsPage),
                                      ('/exportXML', ExportXML),
                                      ('/createCategory',CreateCategory),
                                      ('/addItems',AddItems),
                                      ('/searchItem',SearchItem),
                                      ('/exportIntialXML',ExportIntialXML),
                                      ('/importXML',ImportXML),
                                      ('/importXMLIntial',ImportXMLIntial),
                                      ('/voting',Voting),
                                      ('/result',Results),
                                      ('/createCategoryIntial',CreateCategoryIntial),
                                      ('/searchPageAction',SearchIntialPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()    