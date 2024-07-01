from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


# This code defines a custom token generator for account activation, based on the PasswordResetTokenGenerator. The
# _make_hash_value method generates a hash value used to create the token.

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()
