import stripe
from django.conf import settings

STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
stripe.api_key = STRIPE_SECRET_KEY

def get_stripe_account(user):
    return stripe.Account.retrieve(user.stripe_account_id)

def create_stripe_account(user):
    account = stripe.Account.create(type="express")
    user.stripe_account_id = account.id
    user.save()
    return account

def get_stripe_account_link(user):
    """
    Get URL for user's connected stripe account.
        If user has not onboarded - returns the onboarding link to setup account.
        If user has onboarded - returns the login link to manage the account.

    Args:
        user (Profile): to retrieve stripe_account_id field of user's connected stripe account.

    Returns:
        dict: {
            'onboarding_url': str or None,
            'login_url': str or None
        }

    Raises:
        stripe.error.StripeError: If there is an error retrieving or creating the account.
    """
    
    if not user.stripe_account_id:
        account = create_stripe_account(user)
    else:
        account = get_stripe_account(user)

    # account has onboarded (account manage link)
    if account.details_submitted:
        login_link = stripe.Account.create_login_link(user.stripe_account_id)
        return None, login_link.url
    
    # account has not onboarded (account onboarding link)
    else:
        account_link = stripe.AccountLink.create(
            account=user.stripe_account_id,
            refresh_url=f"{settings.DOMAIN_URL}/account/#bank",
            return_url=f"{settings.DOMAIN_URL}/account/#bank",
            type="account_onboarding"
        )
        return account_link.url, None

def delete_stripe_account(user):
    if user.stripe_account_id:
        stripe.Account.delete(user.stripe_account_id)
        user.stripe_account_id = None
        user.save()