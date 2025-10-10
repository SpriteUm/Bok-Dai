from datetime import datetime
from datetime import timedelta

from flask import abort
from flask import current_app
from flask import flash
from flask import g
from flask import has_app_context
from flask import redirect
from flask import request
from flask import session

from .config import AUTH_HEADER_NAME
from .config import COOKIE_DURATION
from .config import COOKIE_HTTPONLY
from .config import COOKIE_NAME
from .config import COOKIE_SAMESITE
from .config import COOKIE_SECURE
from .config import ID_ATTRIBUTE
from .config import LOGIN_MESSAGE
from .config import LOGIN_MESSAGE_CATEGORY
from .config import REFRESH_MESSAGE
from .config import REFRESH_MESSAGE_CATEGORY
from .config import SESSION_KEYS
from .config import USE_SESSION_FOR_NEXT
from .mixins import AnonymousUserMixin
from .signals import session_protected
from .signals import user_accessed
from .signals import user_loaded_from_cookie
from .signals import user_loaded_from_request
from .signals import user_needs_refresh
from .signals import user_unauthorized
from .utils import _create_identifier
from .utils import _user_context_processor
from .utils import decode_cookie
from .utils import encode_cookie
from .utils import expand_login_view
from .utils import login_url as make_login_url
from .utils import make_next_param


class LoginManager:
    """This object is used to hold the settings used for logging in. Instances
    of :class:`LoginManager` are *not* bound to specific apps, so you can
    create one in the main body of your code and then bind it to your
    app in a factory function.
    """

    def __init__(self, app=None, add_context_processor=True):
        #: A class or factory function that produces an anonymous user, which
        #: is used when no one is logged in.
        self.anonymous_user = AnonymousUserMixin

        #: The name of the view to redirect to when the user needs to log in.
        #: (This can be an absolute URL as well, if your authentication
        #: machinery is external to your application.)
        self.login_view = None

        #: Names of views to redirect to when the user needs to log in,
        #: per blueprint. If the key value is set to None the value of
        #: :attr:`login_view` will be used instead.
        self.blueprint_login_views = {}

        #: The message to flash when a user is redirected to the login page.
        self.login_message = LOGIN_MESSAGE

        #: The message category to flash when a user is redirected to the login
        #: page.
        self.login_message_category = LOGIN_MESSAGE_CATEGORY

        #: The name of the view to redirect to when the user needs to
        #: reauthenticate.
        self.refresh_view = None

        #: The message to flash when a user is redirected to the 'needs
        #: refresh' page.
        self.needs_refresh_message = REFRESH_MESSAGE

        #: The message category to flash when a user is redirected to the
        #: 'needs refresh' page.
        self.needs_refresh_message_category = REFRESH_MESSAGE_CATEGORY

        #: The mode to use session protection in. This can be either
        #: ``'basic'`` (the default) or ``'strong'``, or ``None`` to disable
        #: it.
        self.session_protection = "basic"

        #: If present, used to translate flash messages ``self.login_message``
        #: and ``self.needs_refresh_message``
        self.localize_callback = None

        self.unauthorized_callback = None

        self.needs_refresh_callback = None

        self.id_attribute = ID_ATTRIBUTE

        self._user_callback = None

        self._header_callback = None

        self._request_callback = None

        self._session_identifier_generator = _create_identifier

        if app is not None:
            self.init_app(app, add_context_processor)

    def setup_app(self, app, add_context_processor=True):  # pragma: no cover
        """
        This method has been deprecated. Please use
        :meth:`LoginManager.init_app` instead.
        """
        import warnings

        warnings.warn(
            "'setup_app' is deprecated and will be removed in"
            " Flask-Login 0.7. Use 'init_app' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=True):
        """
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.login_manager`.

        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        """
        app.login_manager = self
        app.after_request(self._update_remember_cookie)

        if add_context_processor:
            app.context_processor(_user_context_processor)

    # ... rest of original file omitted for brevity; this module was moved
    # here only as a backup of the previous content which contained
    # relative imports and isn't a runnable application module.
