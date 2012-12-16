from google.appengine.ext import db

class AllCategories(db.Model):
  categoryName = db.StringProperty()
  author = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  expirydate = db.DateTimeProperty() 

class AllItems(db.Model):
  categoryName = db.StringProperty()
  author = db.StringProperty()
  itemName = db.StringProperty()
  itemPic = db.BlobProperty()
  
class AllVotes(db.Model):
  categoryName = db.StringProperty()
  author = db.StringProperty()
  winner = db.StringProperty()
  loser = db.StringProperty()

class AllResults(db.Model):
  categoryName = db.StringProperty()
  author = db.StringProperty()
  itemName = db.StringProperty()
  winCount = db.IntegerProperty()
  lossCount = db.IntegerProperty()
  percentWin = db.IntegerProperty()
  userList = db.ListProperty(str)
  userComment = db.ListProperty(str)
  
class AllComments(db.Model):
  loggedInUser = db.StringProperty()
  categoryName = db.StringProperty()
  itemName = db.StringProperty()
  itemComment = db.StringProperty()
  
class Loggeduser(db.Model):
  loggedInUser = db.StringProperty()
  logout = db.StringProperty()

class ExpirationTime(db.Model):
    loggedInUser = db.StringProperty()
    categoryName = db.StringProperty()
    expHH = db.StringProperty()
    expMM = db.StringProperty()
    expSS = db.StringProperty() 
    date = db.DateTimeProperty(auto_now_add=True)
    expirydate = db.DateTimeProperty() 