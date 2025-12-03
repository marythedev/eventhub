from django.contrib.auth.decorators import user_passes_test


def anonymous_required(redirect_url='home'):
    """
    Restrict access to views (i.e. login/register) for authenticated users.
        Checks that user is not authenticated in the system.
        Otherwise redirects user to the home page (or provided redirect_url).

    Args:
        redirect_url (str): URL name to redirect authenticated users to.
    """

    return user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=redirect_url,
        redirect_field_name=''
    )
