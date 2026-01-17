def global_sidebar_context(request):
    """
    Context processor to provide global data needed for the sidebar,
    such as the clubs a coordinator manages.
    """
    context = {}
    if request.user.is_authenticated:
        roles = request.user.roles or []
        if 'CLUB_COORDINATOR' in roles or 'CO_COORDINATOR' in roles:
            # Assuming 'coordinated_clubs' is the related name for clubs managed by the user
            # If not, checking User model is needed, but based on role_dashboards.py line 15:
            # coordinator_clubs = request.user.coordinated_clubs.all()
            # This seems correct.
            context['coordinator_clubs'] = request.user.coordinated_clubs.all()
            
    return context
