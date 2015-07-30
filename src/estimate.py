import os
import copy

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import messages

from google.appengine.api import mail

from jinja2 import Environment, FileSystemLoader
import webapp2

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

JINJA_ENVIRONMENT = Environment(
#    loader=PackageLoader('estimate', 'templates'),
    loader=FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def format_currency(value):
    return "${:,.2f}".format(value)

JINJA_ENVIRONMENT.filters.update({
    'format_currency': format_currency,
})

def extra_context(handler, context=None):
    """
    Adds extra context.
    """

    context = context or {}

    return dict({'request': handler.request}, **context)


class Shape(messages.Enum):
    L = 10
    U = 20
    R = 30
    O = 0


class CountertopMaterial(ndb.Model):
    type = ndb.StringProperty(indexed=False)
    cost_per_slab = ndb.FloatProperty(indexed=False)
    color = ndb.StringProperty()
    slab_size_sqft = ndb.FloatProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    labor_cost_per_sqft = ndb.FloatProperty(indexed=False)
    image_filename = ndb.StringProperty(indexed=False)
"""
# Group 1
cm1 = CountertopMaterial()
cm1.populate(type="granite", cost_per_slab=800, color="Cecilia Light", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group1_cecilia_light.JPG")
cm1.put()

cm2 = CountertopMaterial()
cm2.populate(type="granite", cost_per_slab=800, color="Fiorito", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group1_fiorito.JPG")
cm2.put()

cm3 = CountertopMaterial()
cm3.populate(type="granite", cost_per_slab=800, color="Ouro Brazil", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group1_ouro_brazil.JPG")
cm3.put()

cm4 = CountertopMaterial()
cm4.populate(type="granite", cost_per_slab=800, color="Tan Brown", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group1_tan_brown.JPG")
cm4.put()

# Group 2
cm5 = CountertopMaterial()
cm5.populate(type="granite", cost_per_slab=1100, color="Giblee", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group2_giblee.JPG")
cm5.put()

cm6 = CountertopMaterial()
cm6.populate(type="granite", cost_per_slab=1100, color="Juparana Wave", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group2_juparana_wave.JPG")
cm6.put()

cm7 = CountertopMaterial()
cm7.populate(type="granite", cost_per_slab=1100, color="Kashmire Cream", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group2_kashmire_cream.JPG")
cm7.put()

cm8 = CountertopMaterial()
cm8.populate(type="granite", cost_per_slab=1100, color="Sapphire", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group2_sapphire.JPG")
cm8.put()


# Group 3
cm9 = CountertopMaterial()
cm9.populate(type="granite", cost_per_slab=1900, color="Copenhagen", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group3_copenhagen.JPG")
cm9.put()

cm10 = CountertopMaterial()
cm10.populate(type="granite", cost_per_slab=1900, color="Golden Crystal", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group3_golden_crystal.JPG")
cm10.put()

cm11 = CountertopMaterial()
cm11.populate(type="granite", cost_per_slab=1900, color="Thyphoon Bordeaux", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group3_thyphoon_bordeaux.JPG")
cm11.put()

cm12 = CountertopMaterial()
cm12.populate(type="granite", cost_per_slab=1900, color="White Ice", slab_size_sqft=45, labor_cost_per_sqft=50, image_filename="group3_white_ice.JPG")
cm12.put()
"""

 
class Client(ndb.Model):
    email = ndb.StringProperty(indexed=False)
    phone = ndb.StringProperty(indexed=False)
    street1 = ndb.StringProperty(indexed=False)
    street2 = ndb.StringProperty(indexed=False)
    zipcode = ndb.StringProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    message = ndb.TextProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)


class CountertopShape(ndb.Model):
    A = ndb.FloatProperty(indexed=False)
    B = ndb.FloatProperty(indexed=False)
    C = ndb.FloatProperty(indexed=False)
    D = ndb.FloatProperty(indexed=False)
    E = ndb.FloatProperty(indexed=False)
    F = ndb.FloatProperty(indexed=False)
    shape = msgprop.EnumProperty(Shape, required=True)
    sqft = ndb.ComputedProperty(lambda self: self.compute_sqft())
    
    def compute_sqft(self):
        if self.shape == Shape.L:
            return (self.A * self.B + self.C * self.D) / 144.0
        if self.shape == Shape.U:
            return (self.A * self.B + self.F * (self.C - self.E) + self.C * self.D) / 144.0
        if self.shape == Shape.R:
            return (self.A * self.B) / 144.0
        return 0
    
    def get_sides(self):
        if self.shape == Shape.L:
            return (self.A, self.B, self.C, self.D)
        elif self.shape == Shape.R:
            return (self.A, self.B)
        elif self.shape == Shape.U:
            return (self.A, self.B, self.C, self.D, self.E, self.F)
        return ()
    
    def get_name(self):
        if self.shape == Shape.L:
            return 'L-shape'
        elif self.shape == Shape.U:
            return 'U-shape'
        elif self.shape == Shape.R:
            return 'R-shape'
        return 'Shape: other'
    
    def get_path(self):
        if self.shape == Shape.L:
            return '/lshape'
        if self.shape == Shape.U:
            return '/ushape'
        if self.shape == Shape.R:
            return '/rshape'
        return '/contact'

class Estimate(ndb.Model):
    """Sub model for representing an author."""
    client = ndb.StructuredProperty(Client)
    countertop_shapes = ndb.StructuredProperty(CountertopShape, repeated = True)
    total_sqft = ndb.FloatProperty(indexed=False)
    total_price = ndb.FloatProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    need_attention = ndb.BooleanProperty()
    ip = ndb.StringProperty(indexed=False)
    labor_cost = ndb.FloatProperty(indexed=False)
    material = ndb.StructuredProperty(CountertopMaterial) # one for all pieces
    material_cost = ndb.FloatProperty(indexed=False)
    
    def compute_total_sqft(self):
        total = 0
        for shape in self.countertop_shapes:
            total += shape.sqft
        return total
    
    def compute_material_cost(self):
        return (int(self.compute_total_sqft() / self.material.slab_size_sqft) + 1) * self.material.cost_per_slab
    
    def compute_total_price(self):
        return self.compute_material_cost() + self.compute_labor_cost()
    
    def compute_labor_cost(self):
        return self.compute_total_sqft() * self.material.labor_cost_per_sqft
    
    def compute_number_of_slabs(self):
        return int(self.compute_total_sqft() / self.material.slab_size_sqft) + 1

class Order(ndb.Model):
    client = ndb.StructuredProperty(Client)
    estimate = ndb.StructuredProperty(Estimate)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    

class MainPage(webapp2.RequestHandler):

    def get(self):
        # estimates = Estimate.query().order(-Estimate.date_created)
        """
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        """
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(**extra_context(self)))

class TempPage(webapp2.RequestHandler):

    def get(self):
        # estimates = Estimate.query().order(-Estimate.date_created)
        """
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        """
        template = JINJA_ENVIRONMENT.get_template('temp.html')
        self.response.write(template.render(**extra_context(self)))


class ShapeRevertHandler(webapp2.RequestHandler):

    def get(self):
        eid = self.request.get('eid')
        if not eid:
            self.redirect('/')
        
        key = ndb.Key(urlsafe=eid)
        estimate = key.get()
        
        if len(estimate.countertop_shapes) > 0:
            path = estimate.countertop_shapes[-1].get_path()
            new_shapes = copy.copy(estimate.countertop_shapes[:-1])
            estimate.countertop_shapes = new_shapes
            estimate.put()
            
            self.redirect('%s?eid=%s' % (path, estimate.key.urlsafe()))
        else:
            self.redirect('/')
            
class ShapeHandler(webapp2.RequestHandler):
    SHAPED = {'/lshape': 'lshape.html', '/rshape': 'rshape.html', '/ushape': 'ushape.html'}
    
    def get(self):
        name = self.request.path
        template = JINJA_ENVIRONMENT.get_template(self.SHAPED.get(name))
        self.response.write(template.render(**extra_context(self)))
    
    def get_shape(self):
        if self.request.path == '/lshape':
            return Shape.L
        if self.request.path == '/rshape':
            return Shape.R
        if self.request.path == '/ushape':
            return Shape.U
        return Shape.O
    
    def post(self):
        side_A = self.request.get('side_A')
        side_B = self.request.get('side_B')
        side_C = self.request.get('side_C')
        side_D = self.request.get('side_D')
        side_E = self.request.get('side_E')
        side_F = self.request.get('side_F')
        eid = self.request.get('eid')
        shape = self.get_shape()
        
        def _do_redirect():
            self.redirect( "{0}?eid={1}&side_A={2}&side_B={3}&side_C={4}&side_D={5}".
                           format(self.request.path, eid, side_A, side_B, side_C, side_D, side_E, side_F))
        
        if not unicode.isdigit(side_A) or not unicode.isdigit(side_B):
            _do_redirect()
            return
        
        if shape == Shape.L or shape == Shape.U:
            if not unicode.isdigit(side_C) or not unicode.isdigit(side_D):
                _do_redirect()
                
        if shape == Shape.U:
            if not unicode.isdigit(side_E) or not unicode.isdigit(side_F):
                _do_redirect()
                
        # everything is fine
        if eid:
            key = ndb.Key(urlsafe=eid)
            estimate = key.get()
        else:
            estimate = Estimate()
        
        # estimate.material = CountertopMaterial.query()[0]
        piece = CountertopShape(shape=shape)
        # material = CountertopMaterial().query(CountertopMaterial.color == 'black').fetch(1)[0]
        # estimate.material = material
        if side_A: piece.A = float(side_A)
        if side_B: piece.B = float(side_B)
        if side_C: piece.C = float(side_C)
        if side_D: piece.D = float(side_D)
        if side_E: piece.E = float(side_E)
        if side_F: piece.F = float(side_F)
        
        estimate.countertop_shapes.append(piece)
        estimate.total_sqft = estimate.compute_total_sqft()
        # estimate.labor_cost = estimate.compute_labor_cost()
        # estimate.total_price = estimate.compute_total_price()
        estimate.ip = self.request.remote_addr
        estimate.put()
        self.redirect('/material?eid=%s' % estimate.key.urlsafe())


class TotalHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('total.html')
        eid = ndb.Key(urlsafe=self.request.get('eid'))
        mid = ndb.Key(urlsafe=self.request.get('mid'))
        estimate = eid.get()
        material = mid.get()
        estimate.material = material
        estimate.put()
        template_values = { 'estimate': estimate }

        self.response.write(template.render(**extra_context(self, template_values)))
    
    def post(self):
        side_A = self.request.get('side_A')
        side_B = self.request.get('side_B')
        side_C = self.request.get('side_C')
        side_D = self.request.get('side_D')
        eid = self.request.get('eid')
        key = ndb.Key(urlsafe=eid)

        if not unicode.isdigit(side_A) or not unicode.isdigit(side_B) or\
        not unicode.isdigit(side_C) or not unicode.isdigit(side_D):
            self.redirect('/lshape?eid=%s&side_A=%s&side_B=%s&side_C=%s&side_D=%s' % (eid, side_A, side_B, side_C, side_D))
            return
            

        # everything is fine
        if key:
            estimate = key.get()
        else:
            estimate = Estimate()
        
        # estimate.material = CountertopMaterial.query()[0]
        shape = CountertopShape(shape=Shape.L)
        # material = CountertopMaterial().query(CountertopMaterial.color == 'black').fetch(1)[0]
        # estimate.material = material
        shape.A = float(side_A)
        shape.B = float(side_B)
        shape.C = float(side_C)
        shape.D = float(side_D)

        estimate.countertop_shapes.append(shape)
        estimate.total_sqft = estimate.compute_total_sqft()
        # estimate.labor_cost = estimate.compute_labor_cost()
        # estimate.total_price = estimate.compute_total_price()
        estimate.ip = self.request.remote_addr
        estimate.put()
        self.redirect('/material?eid=%s' % estimate.key.urlsafe())


class MaterialHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('material.html')
        l = CountertopMaterial.query()
        template_values = { 'materials': l }

        self.response.write(template.render(**extra_context(self, template_values)))
        return
 

class EstimateHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('estimate.html')
        self.response.write(template.render(**extra_context(self)))

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render(**extra_context(self)))

class AdminHandler(webapp2.RequestHandler):
    def get(self):
        estimates = Estimate.query(Estimate.need_attention == True)

        user = users.get_current_user()
        if not user:
            url = users.create_login_url(self.request.uri)
            self.redirect(url)
            return
        
        """
        if user.nickname() != "admin@admin.com":
            self.response.write("Not authorized")
            return
        """
        
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        template_values = {
            'user': user,
            'estimates': estimates,
            'url': url,
            'url_linktext': url_linktext,
            'user': user
        } 
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))



class ContactHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('contact_other.html')
        self.response.write(template.render(**extra_context(self)))

    def post(self):
        name = self.request.get('name')
        phone = self.request.get('phone')
        email = self.request.get('email')
        message = self.request.get('message')
        eid = self.request.get('eid')
        
        
        client = Client()
        client.name = name
        client.email = email
        client.phone = phone
        client.message = message
        client.put()
        
        if eid:
            key = ndb.Key(urlsafe=eid)
        
            estimate = key.get()
            estimate.client = client
            estimate.need_attention = True
            estimate.total_price = estimate.compute_total_price()
            estimate.total_sqft = estimate.compute_total_sqft()
            estimate.material_cost = estimate.compute_material_cost()
            estimate.labor_cost = estimate.compute_labor_cost()
            
            estimate.put()

            template = JINJA_ENVIRONMENT.get_template('email.html')
            template_values = {
                               'client': client,
                               'estimate': estimate }
            html = template.render(**extra_context(self, template_values))
        else:
            template = JINJA_ENVIRONMENT.get_template('client_details.html')
            template_values = { 'client': client }
            
            html = template.render(**extra_context(self, template_values))
            
        message = mail.EmailMessage(sender="grybkin@gmail.com",
                            subject="New Client")

        message.to = "sergey@domus-surfaces.com"
        message.cc = "sergek@russianamericanmedia.com"
        message.html = html
        message.send()
            
        self.redirect('/thankyou')

class ThankyouHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('thankyou.html')
        self.response.write(template.render(**extra_context(self)))


application = webapp2.WSGIApplication([
#    ('/', TempPage),
    ('/', MainPage),
    ('/estimate', EstimateHandler),
    ('/about', AboutHandler),
    ('/lshape', ShapeHandler),
    ('/ushape', ShapeHandler),
    ('/rshape', ShapeHandler),
    ('/shape', ShapeRevertHandler),
    ('/contact', ContactHandler),
    ('/admin', AdminHandler),
    ('/material', MaterialHandler),
    ('/total', TotalHandler),
    ('/thankyou', ThankyouHandler),
#    ('/rest/.*', rest.Dispatcher),
], debug=debug)


# configure the rest dispatcher to know what prefix to expect on request urls
# rest.Dispatcher.base_url = "/rest"

# add all models from the current module, and/or...
# rest.Dispatcher.add_models_from_module(__name__)
# add all models from some other module, and/or...
# rest.Dispatcher.add_models_from_module(my_model_module)
# add specific models
"""
rest.Dispatcher.add_models({
#  "estimate": Estimate,
  "material": CountertopMaterial})
# add specific models (with given names) and restrict the supported methods

rest.Dispatcher.add_models({
  'material' : (CountertopMaterial, rest.READ_ONLY_MODEL_METHODS),
#  'estimate' : (Estimate, ['GET', 'POST', 'PUT']),
#  'cache' : (CacheModel, ['GET_METADATA', 'GET', 'DELETE'] 
})

# optionally use custom authentication/authorization
# rest.Dispatcher.authenticator = MyAuthenticator()
# rest.Dispatcher.authorizer = MyAuthorizer()

"""
