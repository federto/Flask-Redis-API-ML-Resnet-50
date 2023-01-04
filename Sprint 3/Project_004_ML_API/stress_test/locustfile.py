from locust import HttpUser, task, between


class APIUser(HttpUser):

    # Put your stress tests here.
    # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
    # TODO

    @task
    def home(self):
        self.client.get("/")

    @task(2)
    def predict(self):
        data = {"file": open("dog.jpeg", "rb")}

        self.client.post("/predict", files=data )

    wait_time = between(0.5, 5)

#    raise NotImplementedError
