from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Club, User


@receiver(m2m_changed, sender=Club.coordinators.through)
def handle_club_coordinators_changed(sender, instance, action, pk_set, **kwargs):
	"""
	Handle the addition/removal of club coordinators and update their roles accordingly.
	"""
	if action == 'post_add':
		# Add CLUB_COORDINATOR role to newly added coordinators
		for user_id in pk_set:
			user = User.objects.get(id=user_id)
			if 'CLUB_COORDINATOR' not in user.roles:
				user.roles.append('CLUB_COORDINATOR')
				user.save()
	
	elif action == 'post_remove':
		# Remove CLUB_COORDINATOR role from removed coordinators (if they don't coordinate other clubs)
		for user_id in pk_set:
			user = User.objects.get(id=user_id)
			# Check if user is still a coordinator for other clubs
			if not user.coordinated_clubs.exists() and 'CLUB_COORDINATOR' in user.roles:
				user.roles.remove('CLUB_COORDINATOR')
				user.save()
