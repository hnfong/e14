"""
Paginating function(s)
"""

from urllib.parse import urlencode

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe

def encoded_list(in_dict):
    out_list = []
    for k, l in in_dict.items():
        for v in l:
            if isinstance(v, str):
                v = v.encode('utf-8')

            out_list.append((k, v,))
    return out_list


def paginate(my_list, default_page_size, request, upper_limit=None):
    """Wrapper around django's Paginator, and returns a dictionary containing
    useful stuff. We standardize on some conventions here, eg. use of pgi and
    pgn."""

    params = dict(request.GET) # dictionary of lists of values...
    n = params.get("pgn")
    if n is not None:
        n = int(n[0])
        if upper_limit is None: upper_limit = default_page_size
        if n > upper_limit: n = upper_limit
    else:
        n = default_page_size

    paginator = Paginator(my_list, n)
    idx = params.get('pgi') or [None]
    try:
        paginated_list = paginator.page(idx[0])
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_list = paginator.page(paginator.num_pages)

    if paginated_list.has_next():
        next_params = dict(params)
        next_params["pgi"] = [str(paginated_list.next_page_number())]
        href = urlencode(encoded_list(next_params))
        setattr(paginated_list, "next_href", href)
        setattr(paginated_list, "next_a_start", mark_safe("<a class='paginate-next btn btn-outline-primary' href='?%s'>" % href))
        setattr(paginated_list, "next_a_end", mark_safe("</a>"))
    else:
        setattr(paginated_list, "next_href", "")
        setattr(paginated_list, "next_a_start", mark_safe("<a class='paginate-stop'>"))
        setattr(paginated_list, "next_a_end", mark_safe("</a>"))

    if paginated_list.has_previous():
        previous_params = dict(params)
        previous_params["pgi"] = [str(paginated_list.previous_page_number())]
        href = urlencode(encoded_list(previous_params))
        setattr(paginated_list, "previous_href", href)
        setattr(paginated_list, "previous_a_start", mark_safe("<a class='paginate-previous btn btn-outline-primary' href='?%s'>" % href))
        setattr(paginated_list, "previous_a_end", mark_safe("</a>"))
    else:
        setattr(paginated_list, "previous_href", "")
        setattr(paginated_list, "previous_a_start", mark_safe("<a class='paginate-stop'>"))
        setattr(paginated_list, "previous_a_end", mark_safe("</a>"))

    return paginated_list

