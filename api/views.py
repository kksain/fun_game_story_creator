from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.contrib.auth.models import User
from .models import Story, Contribution
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, StorySerializer, ContributionSerializer
from .tasks import export_story_as_pdf, export_story_as_image


class RegisterView(generics.CreateAPIView):
    """
    API to register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    Handles user login by providing access and refresh tokens.
    """

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    Handles user logout by blacklisting the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(generics.RetrieveAPIView):
    """
    Retrieves the current user's information.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class StoryListCreateView(generics.ListCreateAPIView):
    """
     API to list all stories or create a new story.
    """
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):

        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
     API to retrieve, update, or delete a specific story.
    """
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except NotFound:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            story = self.get_object()
            if story.created_by != request.user:
                raise PermissionDenied(
                    "You do not have permission to edit this story.")
            return super().update(request, *args, **kwargs)
        except NotFound:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        try:
            story = self.get_object()
            if story.created_by != request.user:
                raise PermissionDenied(
                    "You do not have permission to delete this story.")
            return super().destroy(request, *args, **kwargs)
        except NotFound:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class ContributionCreateView(generics.CreateAPIView):
    """
        API to create a contribution for a specific story.
    """
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        story = Story.objects.get(pk=self.kwargs['pk'])

        if story.completed:
            return Response({"error": "This story is already complete."}, status=status.HTTP_400_BAD_REQUEST)

        if story.contributions.count() >= 4:
            story.completed = True
            story.save()
            return Response({"error": "This story has reached the maximum number of contributions and is now complete."}, status=status.HTTP_400_BAD_REQUEST)

        content = request.data.get('content', '').strip()
        if len(content.splitlines()) != 2:
            return Response({"error": "Each contribution must be exactly two lines."}, status=status.HTTP_400_BAD_REQUEST)

        contribution = Contribution(
            story=story, user=request.user, content=content)
        contribution.save()

        if story.contributions.count() == 4:
            story.completed = True
            story.save()

        return Response({"message": "Contribution added successfully."}, status=status.HTTP_201_CREATED)


class ExportStoryView(generics.GenericAPIView):
    """
        API to export a story as a PDF or image.
    """
    queryset = Story.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        story_id = self.kwargs['pk']
        export_type = request.data.get('type', 'pdf')
        story = self.get_object()

        if export_type == 'pdf':
            export_story_as_pdf.delay(story.id)
        elif export_type == 'image':
            export_story_as_image.delay(story.id)
        else:
            return Response({"error": "Invalid export type. Choose 'pdf' or 'image'."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Export started. The file will be available soon."}, status=status.HTTP_202_ACCEPTED)
