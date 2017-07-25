from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings


def get_paginator(objects, page, count=settings.PAGINATION_RECORDS):
    paginator = Paginator(objects, count)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
