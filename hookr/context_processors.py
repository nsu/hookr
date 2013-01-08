from exchange.models import HookrUser

#I'd like to do something like this
# from django.db.models import Sum

# annotated_projects = Project.objects.all().annotate(cost_sum=Sum('cost__cost'))
# for project in annotated_projects:
#     print project.title, project.cost_sum

def default_hookr_context(request):
    context = {}

    if request.user.is_authenticated():
        portfolio = request.user.sharegroup_set.all()
    return context
