# add this in settings.py of the project under templates
def notificationCount(request):
	if 'notif_count' in request.session:
		notif_count = request.session.get('notif_count')
		print('notifCount: ', notif_count)
		return{
			'notif_count' : notif_count
		}
	return{}