import webapp2
import jinja2
import os

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Index(webapp2.RequestHandler):
    def render_index(self):
        t = jinja_env.get_template("index.html")
        content = t.render()
        self.response.write(content)

    def get(self):
        self.render_index()


class Blog(webapp2.RequestHandler):
    def render_blog(self, title="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        t = jinja_env.get_template("blog.html")
        content = t.render(title=title, content=content, error=error, posts=posts)
        self.response.write(content)

    def get(self):
        self.request.get("error")
        self.render_blog()


class NewPost(webapp2.RequestHandler):
    def render_newpost(self, title="", content="", error=""):
        t = jinja_env.get_template("newpost.html")
        content = t.render(title=title, content=content, error=error)
        self.response.write(content)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Post(title=title, content=content)
            a.put()
            idUrl = a.key().id()
            self.redirect("/blog/" + str(idUrl))
        else:
            error = "we need both a title and some content!"
            self.render_newpost(title, content, error)


class PostPage(webapp2.RequestHandler):
    def render_postpage(self, post=""):
        t = jinja_env.get_template("permalink.html")
        content = t.render(post=post)
        self.response.write(content)

    def get(self, id):
        post = Post.get_by_id(int(id))
        if not post:
            return self.error(404)
        self.render_postpage(post=post)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', Blog),
    ("/newpost", NewPost),
    webapp2.Route('/blog/<id:\d+>', PostPage)
], debug=True)
