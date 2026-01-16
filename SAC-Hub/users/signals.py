from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Club, User


@receiver(m2m_changed, sender=Club.coordinators.through)
def handle_club_coordinators_changed(sender, instance, action, pk_set, **kwargs):
	"""
	Handle the addition/removal of club coordinators and update their roles accordingly.
	"""
	
	if action == 'post_add':
		# Add CLUB_COORDINATOR role
		users_to_update = []
		if isinstance(instance, Club):
			# Forward relation: instance is Club, pk_set is User IDs
			users_to_update = User.objects.filter(id__in=pk_set)
		elif isinstance(instance, User):
			# Reverse relation: instance is User, pk_set is Club IDs
			# The user (instance) is becoming a coordinator
			users_to_update = [instance]
			
		for user in users_to_update:
			if 'CLUB_COORDINATOR' not in user.roles:
				user.roles.append('CLUB_COORDINATOR')
				user.save()
	
	elif action == 'post_remove':
		# Remove CLUB_COORDINATOR role
		users_to_check = []
		if isinstance(instance, Club):
			users_to_check = User.objects.filter(id__in=pk_set)
		elif isinstance(instance, User):
			users_to_check = [instance]
			
		for user in users_to_check:
			# Check if user is still a coordinator for other clubs
			if not user.coordinated_clubs.exists() and 'CLUB_COORDINATOR' in user.roles:
				user.roles.remove('CLUB_COORDINATOR')
				user.save()
