import cgi
import os
import random
import datetime

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from Models import *

class FirstPage(webapp.RequestHandler):
  def post(self):
      initChoice = self.request.get('firstChoice')
      loggedInUser = self.request.get('loggedInUser')
      logout = self.request.get('logout')            
      if initChoice == "opt6":    # Search Item / Category
          loggedInUser = self.request.get('loggedInUser')
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
 