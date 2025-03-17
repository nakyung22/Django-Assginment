from pydoc import describe

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.transaction import commit
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from todo.forms import TodoUpdateForm, TodoForm
from todo.models import Todo

# @login_required
def todo_list(request):
    todo_list = Todo.objects.filter(user=request.user).order_by('created_at')
    q = request.GET.get('q') # GET 요청으로부터 q에 담긴 쿼리파라미터를 가져옴
    if q:
        # 만약 쿼리피라미처가 존재하면 todo_list에 해당 쿼러파라미터로 filter를 걸어 조건에 맞는 Todo객체만 가져옵니다.
        todo_list = todo_list.filter(Q(title__icontains=q) | Q(description__icontains=q))
    paginator = Paginator(todo_list, 10) # Pagenator 객체를 인스턴스화 합니다.
    page_number = request.GET.get('page') # GET 요청으로부터 page에 담긴 쿼리파라미터 값을 가져옵니다.
    page_obj = paginator.get_page(page_number) # 가져온 페이지 숫자를 이용해서 페이지에 대한 오브젝트를 가져옵니다.

    context = {'page_obj': page_obj}
    return render(request, 'todo/todo_list.html', context)

def todo_info(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    context = {
        'todo': todo.__dict__ # items 메서드를 사용하기 위해 딕셔너리 형태로 context를 넘겨줍니다.
    }
    return render(request, 'todo/todo_info.html', context)

def todo_create(request):
    form = TodoForm(request.POST or None)
    if form.is_valid():
        # form으로부터 넘겨받은 데이터를 바탕으로 Todo 객체를 저장
        # 데이터베이스에 저장하기 전 user 정보를 추가하기 위해 comit=Flase를 사용
        todo = form.save(commit=False)
        todo.user = request.user # Todo 객체에 user정보를 추가
        todo.save() # user정보가 추가된 Todo 객체를 데이터베이스에 저장
        return redirect(reverse('todo_info', kwargs={'todo_id': todo.pk}))
    context = {
        'form': form,
    }
    return render(request, 'todo/todo_create.html', context)

def todo_update(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    form = TodoUpdateForm(request.POST or None, instance=todo)
    if form.is_valid():
        form.save()
        return redirect(reverse('todo_info', kwargs={'todo_id': todo.pk}))
    context = {
        'form': form,
    }
    return render(request, 'todo/todo_update.html', context)

def todo_delete(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    return redirect(reverse('todo_list'))

def home(request):
    if request.user.is_authenticated:
        return redirect('todo_list')
    return redirect('login')