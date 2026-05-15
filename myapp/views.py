from django.core.serializers import serialize
from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework.decorators import api_view

from .models import Item
from .forms import ItemForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
#Views
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy

#apis
from django.http import JsonResponse
from .serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

# class based api views

class ItemListApiView(APIView):
    def get(self,request):
        items=Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer=ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class ItemDetailApiView(APIView):

    def get_obj(self,id):
        try:
            return Item.objects.get(id=id)
        except Item.DoesNotExist:
            return None

    def get(self,request,id):
        item=self.get_obj(id)
        if not item:
            return Response({"msg":"No Item Found"})
        serializer=ItemSerializer(item)
        return Response(serializer.data)

    def put(self,request,id):
        item=self.get_obj(id)
        if not item:
            return Response({"msg":"No Item Found"})
        serializer=ItemSerializer(item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def delete(self,request,id):
        item=self.get_obj(id)
        if not item:
            return Response({"msg":"No Item Found"})
        item.delete()
        return Response({"msg":"Item Deleted"})

#Generic views for api
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter



#all CRUD operations in single view class
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_fields=['item_name','item_price']
    ordering_fields=['item_name','item_price']
    def perform_create(self, serializer):
        serializer.save(user_name=self.request.user)

#b9c47bf824d4a27916b492e1f6b3a818c1fcc723

class ItemListCreateAPI(generics.ListCreateAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer

class ItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

#fun based api views


@api_view(["GET","POST","DELETE"])
def item_list_json_api(request):
    if request.method=="GET":
        items=Item.objects.all()
        serializer=ItemSerializer(items,many=True)
        return Response(serializer.data)

    elif request.method=="POST":
        serializer=ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

@api_view(["GET","PUT","DELETE"])
def item_detail_api(request,id):
    item = Item.objects.get(id=id)
    if request.method=="GET":
        serializer=ItemSerializer(item)
        return Response(serializer.data)
    elif request.method=="PUT":
        serializer=ItemSerializer(item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    elif request.method=="DELETE":
        item.delete()
        return Response({"message":"Item deleted"})









#manual ser
# def item_list_json(request):
#     items=Item.objects.all().values("id","item_name","item_desc","item_price")
#     return JsonResponse(list(items),safe=False)




















# Create your views here.
@login_required
@vary_on_headers("User-Agent")
def index(request):
    items=Item.objects.all()
    paginator=Paginator(items,per_page=5)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)

    context={
        'page_obj':page_obj,
    }
    return render(request,"myapp/index.html",context)


# class IndexClassView(ListView):
#     model=Item
#     template_name = "myapp/index.html"
#     context_object_name = 'item_list'



@login_required
def detail(request,id):
    item=Item.objects.get(id=id)
    context={
        'item':item
    }
    return render(request,'myapp/detail.html',context)

# class DetailClassView(DetailView):
#     model = Item
#     template_name = 'myapp/detail.html'
#     context_object_name = 'item'



@login_required
def create_item(request):
    form =ItemForm(request.POST or None)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect('myapp:index')

    context={
        'form':form
    }
    return render(request,'myapp/item_form.html',context)

# class CreateItemView(CreateView):
#     #checks for item_form.html
#     model = Item
#     fields = ['item_name','item_desc','item_price','item_image']
#     def form_valid(self,form):
#         form.instance.user_name=self.request.user
#         return super().form_valid(form)


#
@login_required
def update_item(request,id):
    item=Item.objects.get(id=id)
    form=ItemForm(request.POST or None,instance=item)
    if form.is_valid():
        form.save()
        return redirect('myapp:index')
    context={
        'form':form
    }
    return render(request,'myapp/item_update_form.html',context)


# class UpdateItemView(UpdateView):
#     model = Item
#     fields = ['item_name','item_desc','item_price','item_image']
#     template_name_suffix = '_update_form'
#     def get_queryset(self):
#         return Item.objects.filter(user_name=self.request.user)
#
# class DeleteItemView(DeleteView):
#     model = Item
#     success_url=reverse_lazy('myapp:index')


@login_required
def delete_item(request,id):
    item=Item.objects.get(id=id)
    if request.method=="POST":
        item.delete()
        return redirect('myapp:index')
    context={
        'item':item
    }
    return render(request,'myapp/item_delete.html',context)

def get_objects(request):
    items=Item.objects.only('item_name')
    for item in items:
        print(item)