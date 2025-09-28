# Copied from words.hk @ Sep 2025

"""
Contains a bunch of useful/commonly used django stuff. I call this "dj" because
it is sufficiently short.

If you are feeling adventurous, you can do:

from dj import *

Otherwise, just "import dj" and you'll get the stuff.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, JsonResponse, StreamingHttpResponse, FileResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.safestring import mark_safe

def reverse_decorator(f):
    def inner(request, *args, **kwargs):
        return fix_uri_lang(request, f(*args, **kwargs))
    return inner

context_sensitive_reverse = reverse_decorator(reverse)

def fix_uri_lang(context, uri):

    if isinstance(context, str):
        site = context
    else:
        # context is a request object
        site = context.site.domain

    if 'cantowords.com' in site and isinstance(uri, str):
        return fix_uri_lang_force(uri)
    elif 'words.hk' in site and isinstance(uri, str):
        return uri.replace("/dictionary/", "/zidin/")
    else:
        return uri

def fix_uri_lang_force(uri):
    return uri.replace("/zidin/", "/dictionary/")

def app_section(label):
    def labelled_app_section(f):
        f._dj_appsection = label  # pylint: disable=protected-access
        return f
    return labelled_app_section

class NonCachingQuerySetWrapper():
    """Takes a QuerySet and returns a monster

    Background: It's very memory inefficient to paginate up to 50k items. If we
    just pass in the unabridged QuerySet, django **will cache the items** once
    it is iterated. If we pass in the qs.iterator(chunk_size=X) then we lose
    ability to len() and subscript the list. This combines the best of both
    worlds in the worst manner possible. Not sure whether this is future proof
    or not. But hey, it saves memory.

    (And as of writing we're running on an Amazon's T2.micro machines which
    don't have much memory AND doesn't have non-EBS storage so we don't even
    have a swap partition... Ergh -- anyone who questions my decision here
    can first contribute to the server costs, then we can discuss.)
    """
    def __init__(self, orig, size=100):
        self.orig = orig
        self.underlying = orig.iterator(chunk_size=size)

    def __iter__(self):
        return self.underlying.__iter__()

    def __len__(self):
        return self.orig.count()

    def __getitem__(self, value):
        # We know how to slice, but we don't know how to do anything else. We
        # shouldn't need to.
        if isinstance(value, slice):
            return NonCachingQuerySetWrapper(self.orig.__getitem__(value))
        else:
            raise TypeError("MemoryEfficientItemListHack does not support non-slice subscripts")



# Copied from django/middleware/locale (3.x), and butchered by me.
class SiteBasedLocaleMiddleware(MiddlewareMixin):
    """
    Parse a request and decide what translation object to install in the
    current thread context.
    """

    # pylint: disable=no-self-use
    def process_request(self, request):
        from django.conf import settings # pylint: disable=import-outside-toplevel
        domain = get_current_site(request).domain
        language = settings.LANGUAGE_FOR_SITE.get(domain) or settings.LANGUAGE_CODE

        request.IS_BIG_HAN = (language.startswith('zh') or language in ('yue',))

        # Use simplified if user is zh-cn
        if request.IS_BIG_HAN:
            try:
                accept = (request.META.get("HTTP_ACCEPT_LANGUAGE") or "").lower()
                # If zh-cn is in accept and no traditional langs
                if 'zh-cn' in accept:
                    trad_langs = ('zh-hk', 'zh-mo', 'zh-tw', 'yue', 'yue-hk')
                    # Probably this is better, but I don't have time to test it...
                    # if not any(lang in accept for lang in trad_langs):
                    if not any(map(lambda lang: accept.find(lang) != -1, trad_langs)):
                        language = 'zh-cn'
            except Exception as e:
                ERROR("Failed simplified check: %s" % e)

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        response.setdefault('Content-Language', language)
        return response

staff_required = staff_member_required(login_url='/accounts/login')

# Just a workaround to make ruff quiet for the non-used imports
__all__ = [
    "login_required",
    "PermissionDenied",
    "transaction",
    "HttpResponse",
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
    "JsonResponse",
    "StreamingHttpResponse",
    "FileResponse",
    "Http404",
    "render",
    "mark_safe",
    "paginate",
    "DEBUG",
    "INFO",
    "ModelDiffMixin",
    "safer_url_component",
]
"""Convenient django logging methods"""

import logging

logging.basicConfig()  # https://stackoverflow.com/questions/43109355/logging-setlevel-is-being-ignored
default_logger = logging.getLogger("dj")

# pylint: disable=invalid-name
def DEBUG(o):
    default_logger.debug(str(o))

# pylint: disable=invalid-name
def ERROR(o):
    default_logger.error(str(o))

# pylint: disable=invalid-name
def INFO(o):
    default_logger.info(str(o))
"""Helper classes or utilities for models"""

from django.forms.models import model_to_dict

# A really beautiful solution from http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed

class ModelDiffMixin():
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._m2dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._m2dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return list(self.diff.keys())

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._m2dict

    @property
    def _m2dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])
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
"""custom django related utilities"""

def safer_url_component(s):
    """Replaces space with underscore and ampersand with hyphen. This fixes some issues with URL parameters."""
    return s.replace(" ", "_").replace("%", "-")
