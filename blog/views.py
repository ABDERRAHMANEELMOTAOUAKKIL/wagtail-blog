# from django.shortcuts import render
# from blog.models import BlogPage  # Import your BlogPage model

# def search(request):
#     query_string = request.GET.get('q', '')
#     if query_string:
#         # Search for BlogPage instances with titles or content that match the query
#         search_results = BlogPage.objects.live().search(query_string)
#     else:
#         search_results = BlogPage.objects.none()

#     return render(
#         request,
#         'blog/search_results.html',
#         {'search_query': query_string, 'search_results': search_results}
#     )
