from locust import HttpUser, task


class WelcomeUser(HttpUser):
    @task
    def welcome(self):
        self.client.get('/')
        self.client.get("/clubs")
        self.client.post("/show_summary",
                         data={"email": "admin@irontemple.com"})
        self.client.get("/welcome")
        self.client.get('/book/Spring Festival/Simply Lift')
        self.client.post('/purchase_places',
                         data={'club': 'Simply Lift',
                               'competition': 'Fall Classic',
                               'places': '10'})
        self.client.get('/logout')
