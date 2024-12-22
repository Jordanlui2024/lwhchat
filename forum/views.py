from django.shortcuts import render, redirect
from .forms import ForumForm, RelyForm
from .models import ForumModel, ReplyModel
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
def forumListPage(request, page=1):
    search = ""
    listPerPage = 5
    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            (request.user)
            forum = form.save(commit=False)
            forum.author = request.user
            forum.save()
            return redirect('/forum/forumlist/1')
        else:    
            print(forum.error)

    elif request.method == "GET":
        search = request.GET.get("search")
        if search is not None:
           print(search)
           forumdata = ForumModel.objects.filter(title__icontains=search).order_by("-publication_date")
        else:
           print(search)  
           forumdata = ForumModel.objects.all().order_by("-publication_date")
    else:
        forumdata = ForumModel.objects.all().order_by("-publication_date")

    form = ForumForm()
    paginator = Paginator(forumdata, listPerPage)

    forumlist = paginator.get_page(page)
    total_pages = paginator.num_pages
    
    return render(request, "forumListPage.html", {"form": form, "forumlist": forumlist, "page":page, "total_pages":total_pages, "total_range":range(1, total_pages+1), "search":search})

def forumReplyPage(request, forum_id, page=1):
    forum = ForumModel.objects.get(id=forum_id)
    if request.method == "POST":
       form = RelyForm(request.POST)
       if form.is_valid():   
          forum = ForumModel.objects.get(id=forum_id)
          reply = form.save(commit=False)
          reply.forum = forum
          reply.author = request.user
          reply.save()
          forum.replies +=1
          forum.save()
       else:
          print(forum.error)  
    else:
    #    print(forum_id)
       userid = forum.author.id
       if(userid != request.user.id):
          forum.views += 1
          forum.save()
    form = RelyForm()
    replylist = ReplyModel.objects.filter(forum__id=forum_id).order_by("publication_date")
    return render(request, 'forumReplyPage.html', {"form":form, "forum":forum, "replylist":replylist, "forum_id":forum_id, "page":page})



@login_required
def forumArticlePage(request):
    author_id = request.user.pk
    updateid = 0
    if request.method == "POST":
        if 'forumid_del' in  request.POST:
            delid = request.POST['forumid_del']
            del_rec = ForumModel.objects.get(id=delid)
            del_rec.delete()
            form = ForumForm()
        elif 'forumid_edit' in request.POST:
            editid = request.POST['forumid_edit']
            forumdata = ForumModel.objects.get(pk=editid)
            form = ForumForm(instance=forumdata)
            updateid = editid
        else:
            if 'id' in request.POST:
                post_data = request.POST.copy()
                post_data.pop('id', None)
                editid = request.POST.get("id", None)
                forumdata = ForumModel.objects.get(pk=editid)   
                editform = ForumForm(post_data, instance=forumdata)
                editform.save()
                form = ForumForm()
            else:
                form = ForumForm(request.POST)
                if form.is_valid():
                    forum = form.save(commit=False)
                    forum.author = request.user
                    forum.save()
                form = ForumForm()                   
    else:
        form = ForumForm()
                
    forumlist = ForumModel.objects.filter(author__id=author_id).order_by("-publication_date")
    return render(request, "forumArticlePage.html", {"form": form, "forumlist": forumlist, "updateid":updateid})


@login_required
def forumUpdateReplyPage(request, forum_id, page):
    author_id = request.user.pk
    updateid = 0
    if request.method == "POST":
       if 'replyid_del' in request.POST:
          replyid_del = request.POST['replyid_del']
          del_rec = ReplyModel.objects.get(pk=replyid_del)
          del_rec.delete()
        #   print(replyid_del)
          form = RelyForm()
       elif 'replyid_edit' in request.POST:
          editid = request.POST['replyid_edit']
          replydata = ReplyModel.objects.get(pk=editid)
          form = RelyForm(instance=replydata)
          updateid = editid
       else:
          if 'id' in request.POST:
              post_data = request.POST.copy()
              post_data.pop('id', None)
              editid = request.POST.get("id", None)
              replydata = ReplyModel.objects.get(pk=editid)
              editForm = RelyForm(post_data, instance=replydata)  
              editForm.save()
              form = RelyForm()  
    else:
        form = RelyForm()          
    forumreply = ReplyModel.objects.filter(author__id=author_id, forum__id=forum_id).order_by("-publication_date")
    return render(request, "forumUpdateReply.html",{"forumreply":forumreply, "forum_id":forum_id, "page":page, "form":form, "updateid":updateid})