from .forms import StatesSearchForm


def search(request):
    return {'global_search_form': StatesSearchForm()}
