from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Story, Contribution


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ['id', 'story', 'user', 'content', 'created_at']

    def validate_content(self, value):
        if len(value.strip().splitlines()) != 2:
            raise serializers.ValidationError(
                "Each contribution must be exactly two lines.")
        return value


class StorySerializer(serializers.ModelSerializer):
    contributions = ContributionSerializer(many=True, read_only=True)
    created_by = serializers.CharField(
        source='created_by.username', read_only=True)

    class Meta:
        model = Story
        fields = ['id', 'title', 'created_by', 'contributions', 'created_at']
