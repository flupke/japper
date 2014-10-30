from django.core.urlresolvers import reverse

from menu import Menu, MenuItem

# Main menu

Menu.add_item('main', MenuItem(
    'Problems',
    reverse('monitoring_problems'),
    check=lambda request: request.user.is_authenticated()
))

Menu.add_item('main', MenuItem(
    'All states',
    reverse('monitoring_all_states'),
    check=lambda request: request.user.is_authenticated()
))

Menu.add_item('main', MenuItem(
    'Monitoring sources',
    reverse('monitoring_sources'),
    check=lambda request: request.user.is_authenticated()
))

Menu.add_item('main', MenuItem(
    'Alert sinks',
    reverse('monitoring_alert_sinks'),
    check=lambda request: request.user.is_authenticated()
))

# Auth menu

Menu.add_item('auth', MenuItem(
    'Login',
    reverse('login'),
    check=lambda request: not request.user.is_authenticated()
))

Menu.add_item('auth', MenuItem(
    'Profile',
    reverse('users_profile'),
    check=lambda request: request.user.is_authenticated()
))

Menu.add_item('auth', MenuItem(
    'Logout',
    reverse('logout'),
    check=lambda request: request.user.is_authenticated()
))
