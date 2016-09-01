from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify

# These are model managers.
#Post.objects.all()
#Post.objects.create(user=user, title="Sometime")
# You can override the default modermanagers with this.
# Think of (PostManager, self).filter(draft=False) as the original all() and the .filter... as what you append.
class PostManager(models.Manager):
	def active(self, *args, **kwargs):
		#Post.objects.all() = super(PostManager, self).all()
		return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now()) # draft=False makes sure all posts lost in non-draft mode. # Adding publish__lte removes posts in Draft mode from being shown 

# Allows for specifying upload location.
def upload_location(instance, filename): # Allow for my dynamic upload by specifying a user like instance.user or instance.id like we just did here. It is added in Post.image.
	#filebase, extension = filenamd.split('.') # Not a good idea because this would break if the filename had more than one period. 
	#return "%s/%s.%s" %(instance.id, filename, extension) # One would have to autogenerate this, but most likely you will not need something like this.
	return "%s/%s" %(instance.id, filename)

# Create your models here.

class Post(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1) # Value of 1 is that first root admin user.
	title = models.CharField(max_length=120)
	# Just like ImageField there is a FileField. The height_field and width_field require installing pip install pillow.
	# See video File Uploads with FileField & ImageField
	slug = models.SlugField(unique=True) # Slugs video. Point is to not have to use id in our url webpage to see a post. This allows for post to be more shareable.
										 # Required deleting media_cdn pics, database, and migrations under posts/migrations, except for 0001_initial.py.
	image = models.ImageField(null=True, blank=True, upload_to=upload_location, height_field="height_field", width_field="width_field") # blank=True determines whether the field will be required in forms.
	height_field = models.IntegerField(default=0)
	width_field = models.IntegerField(default=0)
	content = models.TextField()
	draft = models.BooleanField(default=False)
	publish = models.DateField(auto_now=False, auto_now_add=False)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False) # Everytime it's saved in DB 'updated' is set. Same as last_updated.
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True) # When entry's added initially not saved, because you can add entry over and over.

	objects = PostManager()

	#def __unicode__(self): #2.x
	def __str__(self):
		return self.title

	# Best practice for URLs, but not a fan of this I prefer URL name approach in next line better.
	# <a href="{% url 'detail' id=obj.id %}">{{ obj.title }}</a><br />
	# Here 'posts' is the namespace and 'detail' is the name URL.
	def get_absolute_url(self):
		return reverse("posts:detail", kwargs={"slug": self.slug})

	# Another option is to order webpage data this way instead of queryset = Post.objects.all().order_by("-timestamp") in views.py.
	class Meta:
		ordering = ["-timestamp", "-updated"]

def create_slug(instance, new_slug=None): # instance is the class Post.
	slug = slugify(instance.title)
	# If new slug is coming thru then slug is that new slug coming in.
	if new_slug is not None:
		slug = new_slug
	# Run the check again to see if slug exists
	qs = Post.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:  # Creates new instance one more time if slug exists.
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	# If it doesnt exist just return back the slug.
	return slug

# Anytime a method(in magic lane) to save is called it will go through this function first to get uploaded filenames automated.
def pre_save_post_receiver(sender, instance, *args, **kwargs): # As in saving a post not the method POST.
	if not instance.slug:
		instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)
