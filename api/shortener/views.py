from typing import Any

from django.core.cache import cache
from rest_framework.generics import get_object_or_404
from django.views.generic import RedirectView
from rest_framework import generics, status
from rest_framework.response import Response


from . import models, serializers
from .models import URL
from .serializers import URLSerializer


class CreateShortURLApiView(generics.CreateAPIView):
    """
    create:
    Creates a short URL from the provided original URL.

    Expects JSON data in the format:
    {
        "url": "http://example.com"
    }

    Where "url" is the original URL that is to be shortened.

    The response contains the original URL and the shortened URL:
    {
        "url": "http://example.com",
        "short_url": "https://peaceful-harbor-90076.herokuapp.com/abcde/"
    }
    """

    queryset = models.URL.objects.all()
    serializer_class = serializers.OriginalURLSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.save()

        cache.set(url.short_url, url.original_url, timeout=60 * 60)

        short_url = URLSerializer(instance=url, context={"request": request})

        return Response(data=short_url.data, status=status.HTTP_201_CREATED)


class ShortUrlRedirectView(RedirectView):
    """
    get:
    Redirects the user to the original URL from the provided short URL.

    Expects the short URL to be part of the path, like:
    https://peaceful-harbor-90076.herokuapp.com/abcde/

    Where "abcd" is the short URL.

    The response is a HTTP 302 redirect to the original URL.
    """

    def get_redirect_url(self, *args: Any, short_url: str, **kwargs: Any) -> str | None:
        url = cache.get(short_url)

        if not url:
            instance = get_object_or_404(URL, short_url=short_url)
            cache.set(instance.short_url, instance.original_url, timeout=60 * 60)
            url = instance.original_url

        return url
