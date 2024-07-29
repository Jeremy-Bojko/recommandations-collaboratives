import pytest
from django.contrib.sites.models import Site
from django_webhook.models import WebhookTopic
from freezegun import freeze_time
from model_bakery import baker

from recoco.apps.geomatics.models import Commune
from recoco.apps.projects.models import Project

from ..models import WebhookSite
from ..signals import WebhookSignalListener


@pytest.fixture
def webhook():
    webhook_topic, _ = WebhookTopic.objects.get_or_create(name="topic")

    webhook = baker.make("django_webhook.Webhook", active=True)
    webhook.topics.add(webhook_topic)

    WebhookSite.objects.create(site=Site.objects.first(), webhook=webhook)
    yield webhook


@pytest.fixture
def commune():
    return baker.make(
        Commune,
        name="Bayonne",
        insee="64102",
        postal="64100",
        latitude=43.4933,
        longitude=-1.4753,
        department__code="64",
        department__name="Pyrénées-Atlantiques",
    )


@pytest.fixture
def project(commune, make_project):
    with freeze_time("2024-05-22"):
        project = make_project(
            name="My project",
            org_name="My organization",
            commune=commune,
            description="My description",
        )
        yield project


@pytest.fixture
def serialized_project(project):
    return {
        "id": project.id,
        "name": "My project",
        "description": "My description",
        "inactive_since": None,
        "created_on": "2024-05-22T02:00:00+02:00",
        "updated_on": "2024-05-22T02:00:00+02:00",
        "org_name": "My organization",
        "switchtenders": [],
        "commune": {
            "name": "Bayonne",
            "insee": "64102",
            "postal": "64100",
            "department": {"name": "Pyrénées-Atlantiques", "code": "64"},
            "latitude": 43.4933,
            "longitude": -1.4753,
        },
        "recommendation_count": 0,
        "public_message_count": 0,
        "private_message_count": 0,
        "project_sites": [
            {
                "id": project.project_sites.current().pk,
                "site": 1,
                "is_origin": True,
                "status": "READY",
            }
        ],
    }


def build_listener():
    return WebhookSignalListener(
        signal=None, signal_name="post_save", model_cls=Project
    )


@pytest.mark.django_db
def test_find_webhooks_ok(webhook, project):
    assert build_listener().find_webhooks("topic", project) == [
        (webhook.id, webhook.uuid)
    ]


@pytest.mark.django_db
def test_find_webhooks_not_active(webhook, project):
    webhook.active = False
    webhook.save()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_topics(webhook, project):
    webhook.topics.clear()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_sites(webhook, project):
    project.sites.clear()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_project():
    task = baker.make("tasks.Task")
    assert build_listener().find_webhooks("topic", task) == []


@pytest.mark.django_db
def test_model_dict_project(project, serialized_project):
    assert build_listener().model_dict(project) == serialized_project


@pytest.mark.django_db
def test_model_dict_taggeditem(project, serialized_project):
    tagged_item = baker.make("taggit.TaggedItem", content_object=project)
    assert build_listener().model_dict(tagged_item) == serialized_project


@pytest.mark.django_db
def test_model_dict_answer(project):
    with freeze_time("2024-05-22"):
        answer = baker.make(
            "survey.Answer",
            question__text="question",
            session__project=project,
        )

    assert build_listener().model_dict(answer) == {
        "id": answer.id,
        "created_on": "2024-05-22T02:00:00+02:00",
        "updated_on": "2024-05-22T02:00:00+02:00",
        "question": {
            "id": answer.question_id,
            "text": "question",
            "text_short": "",
            "slug": "question",
            "is_multiple": False,
            "choices": [],
        },
        "session": answer.session_id,
        "project": project.id,
        "choices": [],
        "values": [],
        "comment": "",
        "signals": "",
        "updated_by": None,
        "attachment": None,
    }


def test_model_dict_other():
    assert build_listener().model_dict(instance="dummy") == {}
