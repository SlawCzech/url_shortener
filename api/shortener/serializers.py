from rest_framework import serializers
import shortuuid

from .models import URL


class URLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = URL
        fields = ("short_url",)

    def get_short_url(self, obj):
        return self.context.get("request").build_absolute_uri("/") + obj.short_url


class OriginalURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ("original_url",)

    def save(self, **kwargs):
        original_url = self.validated_data.get("original_url")
        url = URL(original_url=original_url, short_url=shortuuid.uuid(name=original_url))
        url.save()

        return url
