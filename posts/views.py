
try:
    from urllib import quote_plus #python 2
except:
    pass

try:
    from urllib.parse import quote_plus #python 3
except: 
    pass

from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect 
# redirect will ultimately return a HttpResponseRedirect can accept a model, view, or url 
# as it's "to" argument. So it is a little more flexible in what it can "redirect" to. 
# I also like how redirect is shorter. So I'd use redirect over HttpResponseRedirect.
# Both are fine to use though.


from .models import Post
from .forms import PostForm

# Create your views here.

def post_list(request): # list items
	# if request.user.is_authenticated():
	# 	context = { 'title': 'My User List' }
	# else:
	# 	context = { 'title': 'List' }

	today = timezone.now().date()
	queryset_list = Post.objects.active() #.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		queryset_list = Post.objects.all()

	query = request.GET.get('q')
	if query:
		queryset_list = queryset_list.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(user__first_name__icontains=query) |
			Q(user__last_name__icontains=query) 
			).distinct()

	paginator = Paginator(queryset_list, 4) # Show 25 contacts per page
	page_request_var = 'abc'
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)

	context = { 'object_list': queryset, 'title': 'List', 'page_request_var': page_request_var, 'today': today }
	return render(request, 'post_list.html', context)
	#return HttpResponse('<h1>List</h1>')

def post_detail(request, slug=None): # retrieve
	instance = get_object_or_404(Post, slug=slug) # Has nothing to do with get_absolute_url in models.py.
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.content)
	context = { 'title': instance.title, 'instance': instance, 'share_string': share_string }
	return render(request, 'post_detail.html', context)

def post_create(request):
	# if not request.user.is_staff or not request.user.is_superuser:
	# 	raise Http404
	
	'''If one is not logged in this will get you 'page not found' otherwise this ugly error
	Cannot assign "<SimpleLazyObject: <django.contrib.auth.models.AnonymousUser object at 0xb4fcb70c>>": "Post.user" must be a "User" instance.'''
	# if not request.user.is_authenticated():
	# 	raise Http404
	form = PostForm(request.POST or None, request.FILES or None) # None removes 'This field is required.' message from form page everytime Chrome loads it.
																 # request.FILES or None was added in video "File Uploads with FileField & ImageField/
																 # When Django handles a file upload, the file/image data ends up placed in request.FILES
	if form.is_valid(): # Once you hit create(POST) button it checkt for form fields filled out correctly by user.
		instance = form.save(commit=False)
		instance.user = request.user # Assumes user is logged in.
		#print(form.cleaned_data.get('title')) # Print the data before saving.
		instance.save()
		# Success message forthcoming
		messages.success(request, 'Successfully Created.') # Used in messages_display.html
		# For HttpResponseRedirect the first argument can only be a url.
		return HttpResponseRedirect(instance.get_absolute_url()) # Takes you to the page you just created.

	# Test if the data is coming through.
	# form = PostForm()
	# if request.method == 'POST':
	# 	#print(request.POST)
	# 	print(request.POST.get("title"))
	# 	print(request.POST.get("content"))
	context = { 'form': form, }
	return render(request, 'post_form.html', context)

def post_update(request, slug=None): # To go back and edit posts.
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug) # Has nothing to do with get_absolute_url in models.py.
	form = PostForm(request.POST or None, request.FILES or None, instance=instance) # None removes 'This field is required.' message from form page everytime Chrome loads it.
																					# When Django handles a file/image upload, the file data ends up placed in request.FILES
	print(instance)
	if form.is_valid(): # Form fields filled out correctly by user.
		instance = form.save(commit=False)
		instance.save()
		# Success message forthcoming
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		# For HttpResponseRedirect the first argument can only be a url.
		return HttpResponseRedirect(instance.get_absolute_url()) # Takes you to the page you just updated.

	context = { 'title': instance.title, 'instance': instance, 'form': form, }
	return render(request, 'post_form.html', context)

def post_delete(request, slug=None): # 
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, 'Successfully deleted')
	return redirect("posts:list")
