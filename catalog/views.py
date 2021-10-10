from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Book, Author, BookInstance, Genre, Language
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms.widgets import SelectDateWidget
from django import forms
# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    """View function for home page of the site"""

    #generate couts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (staturs = "a")
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    # THe "all()" is implied by default
    num_authors = Author.objects.all().count()

    # Number if visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }

    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    # your own name for the list as a template variable
    # By default template variable named "object_list" OR "book_list" (i.e. generically "the_model_name_list").
    #context_object_name = 'my_book_list'

    #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    #template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to the current user"""
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).\
            filter(status__exact="o").\
            order_by("due_back")


class LoanedBooksByLibrarianListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to the current librarian"""
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_librarian.html"
    permission_required = ('catalog.can_mark_returned',)
    redirect_field_name = 'catalog'  # redirect to "catalog" page if dont have permissions
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").\
            order_by("due_back")



@login_required
@permission_required("catalog.can_renew", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # if data is being submitted (POST request)
    if request.method == "POST":
        
        # create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)

        # check if the form is valid
        if form.is_valid():
            # process  the data in form.cleaned_data as required
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL
            return HttpResponseRedirect(reverse("all-borrowed"))  # we use "reverse" in function-based view (FBV)
        else:
            # If the form is not valid we call render() again,
            # but this time the form value passed in the context will include error messages.
            pass
    
    # if this is a GET (or any other  method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})
    

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render (request, "catalog/book_renew_librarian.html", context=context)



class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = ('catalog.can_modify_authors',)
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    #initial = {'date_of_death': '11/06/2020'}
    def get_form(self):
        '''add date picker in forms'''
        form = super(AuthorCreate, self).get_form()
        form.fields['date_of_birth'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_death'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = ('catalog.can_modify_authors',)
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    def get_form(self):
        '''add date picker in forms'''
        form = super(AuthorUpdate, self).get_form()
        form.fields['date_of_birth'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_death'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = ('catalog.can_modify_authors',)
    success_url = reverse_lazy('authors')  # reverse_lazy instead of reverse, because class-based view (CBV) attribute







class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = ('catalog.can_renew',)
    fields = "__all__"


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = ('catalog.can_renew',)
    fields = '__all__' # Not recommended (potential security issue if more fields added)


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = ('catalog.can_renew',)
    success_url = reverse_lazy('books')  # reverse_lazy instead of reverse, because class-based view (CBV) attribute