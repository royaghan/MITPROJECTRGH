from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls.base import reverse_lazy
from main import views
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from main.views import AddCommentLike, AddCommentDislike, \
    CommentReplyView, CommentDeleteView, ProfileEditView

urlpatterns = [
                  path('', views.index, name='index'),
                  path('signin', views.signin, name='signin'),
                  path('signup', views.signup, name='signup'),
                  path('logout', views.logout, name='logout'),
                  path('settings', views.settings, name='settings'),
                  path('upload', views.upload, name='upload'),
                  path('explore', views.explore),
                  path('follow', views.follow, name='follow'),
                  path('search', views.search, name='search'),
                  path('profile/<str:pk>', views.profile, name='profile'),
                  path('notifications/', views.ShowNotifications, name='show-notifications'),
                  path('<noti_id>/delete', views.DeleteNotification, name='delete-notification'),
                  path('notifications/', views.notifications_view, name='notifications'),
                  path('notifications/count/', views.notification_count, name='notification_count'),
                  path('like-post/', views.like_post, name='like-post'),
                  path('<uuid:post_id>', views.PostDetails, name='post-details'),
                  path('post/update/<str:id>/', views.update_post, name='post-update'),
                  path('post/delete/<str:id>', views.PostDeleteView, name='post-delete'),
                  path('post/<uuid:post_id>/comment/delete/<int:pk>/', CommentDeleteView.as_view(),
                       name='comment-delete'),
                  path('post/<uuid:post_id>/comment/<int:pk>/like', AddCommentLike.as_view(), name='comment-like'),
                  path('post/<uuid:post_id>/comment/<int:pk>/dislike', AddCommentDislike.as_view(),
                       name='comment-dislike'),
                  path('post/<uuid:post_id>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
                  path('<uuid:post_id>/', views.toggle_comments, name='toggle_comments'),
                  path('re_enable/<uuid:post_id>/', views.re_enable_comments, name='re_enable_comments'),
                  path('profile/<int:pk>/edit', ProfileEditView, name='profile_edit'),

                  path('aboutPage/', views.about_view, name='aboutPage'),
                  path('privacy/', views.privacy_view, name='privacy'),
                  path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
                  path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
                  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),
                  path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(),
                       name='password_reset_complete'),
                  # path('social/signup/', views.signup_redirect, name='signup_redirect'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

