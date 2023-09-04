from django.db import models
from django.db.models import Q
from wagtail.models import Page,Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel
from modelcluster.fields import ParentalKey,ParentalManyToManyField
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager
from django import forms
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator


@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

     # add the get_context method:
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)

        search_keywords = request.GET.get('query', '')#second one for empty research 

        # blogpages = self.get_children().live().filter(title__exact=search_keywords).order_by('-first_published_at')
        blogpages = self.get_children().specific().live().filter(
            Q(title__icontains=search_keywords) # | Q(intro__icontains=search_keywords)
        ).order_by('-first_published_at')

        #pagination
        per_page = 1
        paginator = Paginator(blogpages, per_page) 
        page = request.GET.get("page")
        try:
            blogpages = paginator.page(page)
        except PageNotAnInteger:#if the user type 1BC in the url itll be directed to the first page
            blogpages = paginator.page(1)
        except EmptyPage:
            blogpages = paginator.page(paginator.num_pages)#return the last page of the user write 99999 ex
        # context["posts"]= posts
 
        # print(blogpages)
        context['blogpages'] = blogpages
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
# ... Keep the definition of BlogIndexPage model and add a new BlogPageTag model
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField('blog.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    # Add the main_image method:
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),

            # Add this:
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

