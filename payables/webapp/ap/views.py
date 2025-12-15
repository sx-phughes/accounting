from django.shortcuts import render
from django.http import HttpResponse
from models import Invoices

# Create your views here.


def index(request):

    return render(request, "ap/index.html")
