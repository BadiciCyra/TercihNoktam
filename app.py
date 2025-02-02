from flask import Flask,redirect,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
from universities import university
import os

#Change this to openai.api_key ="YOUR_API_KEY"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)



class Topic(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    topic = db.Column(db.String , nullable = False)
    description = db.Column(db.String , nullable = False)
    
class Comment(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    text = db.Column(db.String , nullable = False)
    topicId = db.Column(db.String , nullable = False)    
    
    
with app.app_context():
    db.create_all()    

def get_uni_reccoms(prompt):
    try:
        response = openai.ChatCompletion.create(
             model="gpt-3.5-turbo",  # Modeli doğru şekilde seçiyoruz
            messages=[
                {"role": "system", "content": "Sen bir üniversite öneri motorusunuz. Kullanıcının isteklerine göre üniversiteleri öneriyorsunuz."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        print("Response: ", response)
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Bir hata oluştu."   



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index.html")
def home_page():
    return render_template("index.html")


#@app.route("/ogrenci_formu.html")
#def student_form():
    #return render_template("blog.html")

@app.route("/AIChat.html" , methods = ["GET" , "POST"])
def ai_chat():
    if request.method == "POST":
        data = request.get_json()
        prompt = data.get("prompt")
        recommendation = get_uni_reccoms(prompt)

        return jsonify({"recommendation": recommendation})  # JSON yanıt gönder

    return render_template("AIChat.html",recommendation=None)


@app.route("/ogrenci_formu.html",methods = ["GET" , "POST"])
def student_forum():
    if request.method == "POST":
        topic = Topic(
            topic = request.form["topic"],
            description = request.form["description"]
        )
        db.session.add(topic)
        db.session.commit()
    topics = db.session.execute(db.select(Topic)).scalars()
    return render_template("blog.html" , topics=topics)  


@app.route("/topic/<int:id>", methods=["GET" , "POST"])
def comments(id):
    if request.method == "POST":
        comment = Comment(
            text = request.form["text"],
            topicId = id
        )
        db.session.add(comment)
        db.session.commit()
    topic = db.get_or_404(Topic,id)
    comments = Comment.query.filter_by(topicId = id).all()
    for comment in comments:
        print(comment)
    return render_template("topic.html" , topic=topic,comments=comments)


@app.route("/delete/<int:id>" ,methods=["POST" ,"DELETE"])
def delete_topic(id):
     topic_deleted = Topic.query.get_or_404(id)
     try:
         db.session.delete(topic_deleted)
         db.session.commit()
         return redirect("/ogrenci_formu.html")
     except Exception as e:
        return f"ERROR:{e}"


@app.route("/comment/delete/<int:id>", methods=["GET", "POST", "DELETE"])
def delete_comment(id):
    comment_deleted = Comment.query.get_or_404(id)  # Eğer id yoksa otomatik 404 döndürür
    
    try:
        db.session.delete(comment_deleted)
        db.session.commit()
        return redirect("/ogrenci_formu.html")  # Doğru yönlendirme
    except Exception as e:
        return f"Error: {e}"  # Hatalı olan `"Not Found"` kaldırıldı
   
    
    
if __name__ in "__main__":
    app.run(debug=True)