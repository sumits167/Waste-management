from flask import Flask,render_template,request,jsonify,redirect,url_for
from functools import wraps

import pymongo

import bcrypt

from bson import ObjectId

from datetime import date,datetime

from unique_id import get_unique_id

import short_unique_id as suid

import uuid

from model.Trainmodel import mod

d=date.today()
dt=datetime.combine(d,datetime.min.time())


client=pymongo.MongoClient("mongodb://127.0.0.1:27017")

db=client["WasteManage"]

users_Collection=db["Users"]
records_collection=db["records"]


print("users_Collection=",users_Collection)

app=Flask(__name__)

email={}
password={}

loginAuth={
     
}

addRecordMessage={

}     


def authentication(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            if "user" in loginAuth:
                return func(*args,**kwargs)
            else:
                return redirect(url_for("Home"))


            
        return wrapper



@app.route('/')
def Home():
    if "user" in loginAuth:
         return redirect(url_for("index"))
    else:
        return render_template('login.html')

@app.route('/signup',methods=["GET","POST"])
def signup():
    if "user" in loginAuth:
         return redirect(url_for("index"))
    else:
      Username=request.form.get("Username")
      Mobile=request.form.get("Mobile")
      Email=request.form.get("Email")
      password=request.form.get("password")
      

      alresyExist=users_Collection.find_one({"Email":Email})
      print("alresyExist=",alresyExist)
      if alresyExist:
            return render_template("signup.html",result="falses")

      if password:
               password_bytes=password.encode("utf-8")
               hashed=bcrypt.hashpw(password_bytes,bcrypt.gensalt())

               print(Username)
               print(Mobile)
               print(Email)
               print(password)
               result = users_Collection.insert_one({
                     "Username":Username,
                     "Mobile":Mobile,
                     "Email":Email,
                     "password":hashed
           
                })
               print("Result==",result)
               return render_template("signup.html",result="Successs")
      else:
          return render_template("signup.html",result="false")


      
@app.route('/handleSignup')
def handleSignup():
     pass


# @app.route('/login',methods=["POST"])
# def login():
#     return render_template("login.html")



@app.route("/home")
@authentication
def index():
        print("Hello2")
        records=records_collection.find_one({"userId":loginAuth["user"]["_id"]})
        total_Amount=list(records_collection.aggregate([
             {"$match":{"userId":ObjectId(loginAuth["user"]["_id"])}},
             {
                  "$set":{
                       "totalAmount":{
                            "$sum":{
                                 "$map":{
                                      "input":"$allRecords",
                                      "as":"rec",
                                      "in":"$$rec.amountEarned"
                                 }
                            }
                       }
                  }
             },
             {
                  "$project":{
                       "totalAmount":"$totalAmount"
                       
                  }
             }
        ]))
        print("TotalAmount==",total_Amount)
        if(len(total_Amount)==0):
             total_Amount=[{}]
        print("record=",records)
        return render_template("allRecords.html",user=loginAuth["user"],records=records,total_Amount=total_Amount)
   



@app.route('/handleLogin',methods=["post"])
def handleLogin():
    
    
    email["email"]=request.form["email"]
    password["password"]=request.form["password"]
    print(email)
    print(password)
    findUser=users_Collection.find_one({"Email":email["email"]})
    print("FindUser=",findUser)
    if(findUser):
         print("FinPass==",findUser["password"])
         hashpass=findUser["password"]
         password_bytes=password["password"].encode("utf-8")

         if bcrypt.checkpw(password_bytes,hashpass):
               loginAuth["user"]=findUser
               return redirect(url_for("index"))
         
    return render_template("Login.html",result="Login failed")         

     

# @app.route('/home',methods=["post"])
# def Home():
#     return render_template("index.html")


@app.route('/logout',methods=["post"])
def logout():
     loginAuth.pop("user",None)
     return redirect(url_for("Home"))
     

@app.route('/addRecords')
def  addRecords():
     return render_template("index.html",addRecordMessage=addRecordMessage)

@app.route('/record')
def records():
     addRecordMessage["Success"]=None
     addRecordMessage["failed"]=None
     return redirect("addRecords")


@app.route('/handleAddRecords',methods=["GET","POST"])
def handleAddRecords():
     print("pip install uuid=",uuid.uuid4())
     wasteType=request.form.get("waste_type")
     Weight=float(request.form.get("weight"))
     # amountEarned=int(request.form.get("amount"))

     mod_res=mod(wasteType,Weight)
     print("Model_response=",mod_res)
     if mod_res=="Unknown Plastic Type":
                    addRecordMessage["failed"]="Unknown Waste type"
                    addRecordMessage["Success"]=None
                    return redirect("addRecords")

     
     print("RecorsdDetails=")
     print(wasteType)
     print(Weight)
     # print(amountEarned)

     if wasteType:
               findRes=records_collection.find_one({"userId":ObjectId(loginAuth["user"]["_id"])})
               print("findResfindRes==",findRes)
               if(findRes):
                    rec_res=records_collection.update_one(
                         {"userId":ObjectId(loginAuth["user"]["_id"])},
                         {"$push":{'allRecords':{"wasteType":wasteType,"Weight":Weight,"amountEarned":mod_res,"date":dt,"id":str(uuid.uuid4())}}}
                         )
                    print("RecordPushResult=",rec_res)
                    addRecordMessage["Success"]=mod_res
                    addRecordMessage["failed"]=None

               else:
                    cre_res=records_collection.insert_one(
                         {
                              "userId":ObjectId(loginAuth["user"]["_id"]),
                              "allRecords":[
                                   {"wasteType":wasteType,"Weight":Weight,"amountEarned":mod_res,"date":dt}

                              ]

                        }
                   )
                    print("Create Res=",cre_res)
                    addRecordMessage["Success"]=mod_res
                    addRecordMessage["failed"]=None
                    
     else:
          print("Details not found")
          addRecordMessage["failed"]="Something went wrong try again"
          addRecordMessage["Success"]=None




     return redirect("addRecords")


@app.route('/delete/<path:record_id>',methods=["POST"])
def deleteRecord(record_id):
     print("id=",record_id)
     print("LOGINAUTH=",loginAuth)
     print("_id=",loginAuth["user"]["_id"])
     record_delete=records_collection.update_one(
          {"userId":ObjectId(loginAuth["user"]["_id"])},
          {"$pull":{"allRecords":{"id":record_id}}}
          )
     
     print("record_delete_Result=",record_delete)
     return redirect(url_for("index"))

if __name__=="__main__":
    app.run(port=5000,debug=True)














