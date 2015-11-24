# -*- coding: utf-8 -*-
import pit
import miniconfig
import tornado.web
import tornado.gen
import tornado.auth
import tornado.ioloop


credentials = pit.Pit.get('python-google-auth-example', {'require': {
    'client_id': '???',
    'client_secret': '???',
}})


redirect_url = 'http://localhost:8000/redirect'



class Configurator(miniconfig.ConfiguratorCore):
    def __init__(self, *args, **kwds):
        super(Configurator, self).__init__(*args, **kwds)

        if 'routes' not in self.settings:
            self.settings['routes'] = []

    def add_route(self, route, handler):
        self.settings['routes'].append((route, handler))

    def make_app(self):
        self.commit()
        app = tornado.web.Application(self.settings.get('routes', []))
        app.listen(8000)
        tornado.ioloop.IOLoop.current().start()


class GoogleOAuth2RedirectEndpointHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('GET')

    def post(self):
        self.write('POST')


class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=redirect_url,
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            # Save the user and access token with
            # e.g. set_secure_cookie.
        else:
            yield self.authorize_redirect(
                redirect_uri=redirect_url,
                client_id=credentials['client_id'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


def includeme(config):
    config.add_route('/', GoogleOAuth2LoginHandler)
    config.add_route('/redirect', GoogleOAuth2RedirectEndpointHandler)


def main():
    config = Configurator()
    config.include(includeme)
    app = config.make_app()

if __name__ == '__main__':
    main()
