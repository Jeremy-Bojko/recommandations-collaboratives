# encoding: utf-8

"""
tests for digesting emails

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-02-03 16:14:54 CET
"""

import test  # noqa

import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import models as notifications_models
from notifications.models import Notification
from notifications.signals import notify
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.projects import signals as projects_signals
from urbanvitaliz.apps.tasks import signals as tasks_signals
from urbanvitaliz.apps.resources import models as resources_models
from urbanvitaliz.apps.tasks import models as tasks_models
from urbanvitaliz import verbs

from .. import digests

########################################################################
# new reco digests
########################################################################


@pytest.mark.django_db
def test_send_digests_for_new_reco(client, request):
    membership = baker.make(projects_models.ProjectMember)

    switchtender = Recipe(
        auth.User, username="advisor", email="advisor@example.com"
    ).make()

    project = baker.make(
        projects_models.Project,
        sites=[get_current_site(request)],
        status="DONE",
        projectmember_set=[membership],
    )

    # Generate a notification
    tasks_signals.action_created.send(
        sender=test_send_digests_for_new_reco,
        task=tasks_models.Task.objects.create(
            project=project, site=get_current_site(request), created_by=switchtender
        ),
        project=project,
        user=switchtender,
    )

    digests.send_digests_for_new_recommendations_by_user(
        membership.member, dry_run=False
    )

    assert membership.member.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_send_digests_for_new_reco_empty(client):
    membership = baker.make(projects_models.ProjectMember)

    baker.make(projects_models.Project, status="DONE", projectmember_set=[membership])

    digests.send_digests_for_new_recommendations_by_user(
        membership.member, dry_run=False
    )

    assert membership.member.notifications.unsent().count() == 0


########################################################################
# new sites digests
########################################################################


@pytest.mark.django_db
def test_send_digests_for_new_sites_by_user(request):
    current_site = get_current_site(request)

    advisor_group = auth.Group.objects.get(name="example_com_advisor")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(advisor_group)
    regional_actor.profile.departments.add(dpt_nord)
    regional_actor.profile.sites.add(current_site)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(advisor_group)
    non_regional_actor.profile.departments.add(dpt_npdc)
    non_regional_actor.profile.sites.add(current_site)

    # moderator
    moderator = Recipe(auth.User).make()

    membership = baker.make(projects_models.ProjectMember, is_owner=True)
    project = baker.make(
        projects_models.Project,
        projectmember_set=[membership],
        commune=commune,
        status="READY",
        sites=[current_site],
    )

    # Generate a notification
    projects_signals.project_validated.send(
        sender=projects_models.Project,
        site=current_site,
        moderator=moderator,
        project=project,
    )

    assert regional_actor.notifications.unsent().count() == 1
    assert non_regional_actor.notifications.unsent().count() == 0

    digests.send_digests_for_new_sites_by_user(regional_actor)
    digests.send_digests_for_new_sites_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_send_digests_for_switchtender_by_user(request, client):
    current_site = get_current_site(request)

    advisor_group = auth.Group.objects.get(name="example_com_advisor")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    organization = Recipe(addressbook_models.Organization, name="Orga").make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.profile.sites.add(current_site)
    regional_actor.profile.organization = organization
    regional_actor.profile.save()
    regional_actor.groups.add(advisor_group)
    regional_actor.profile.departments.add(dpt_nord)

    regional_actor2 = Recipe(auth.User).make()
    regional_actor2.groups.add(advisor_group)
    regional_actor2.profile.departments.add(dpt_nord)
    regional_actor2.profile.sites.add(current_site)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(advisor_group)
    non_regional_actor.profile.departments.add(dpt_npdc)
    non_regional_actor.profile.sites.add(current_site)

    membership = baker.make(projects_models.ProjectMember, is_owner=True)
    project = baker.make(
        projects_models.Project,
        projectmember_set=[membership],
        commune=commune,
        status="READY",
    )

    # Generate a notification
    projects_signals.project_switchtender_joined.send(
        sender=regional_actor, project=project
    )

    assert (
        regional_actor.notifications.unsent().count() == 0
    )  # shouldn't get her own action notified
    assert regional_actor2.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0
    assert membership.member.notifications.unsent().count() == 1

    digests.send_digest_for_switchtender_by_user(regional_actor)
    digests.send_digest_for_switchtender_by_user(regional_actor2)
    digests.send_digest_for_switchtender_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert regional_actor2.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_notification_formatter():
    formatter = digests.NotificationFormatter()

    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    organization = Recipe(addressbook_models.Organization, name="DuckCorp").make()
    user.profile.organization = organization
    user.profile.save()
    recipient = Recipe(auth.User).make()
    resource = Recipe(resources_models.Resource, title="Belle Ressource").make()
    task = Recipe(
        tasks_models.Task,
        intent="my intent",
        content="A very nice content",
        resource=resource,
    ).make()
    public_note = Recipe(projects_models.Note, content="my content", public=True).make()
    private_note = Recipe(
        projects_models.Note, content="my content", public=False
    ).make()

    followup = Recipe(tasks_models.TaskFollowup, task=task, comment="Hello!").make()
    project = Recipe(
        projects_models.Project,
        name="Nice Project",
        description="Super description",
        location="SomeWhere",
    ).make()

    tests = [
        (
            verbs.Conversation.PUBLIC_MESSAGE,
            public_note,
            (
                f"Bobi Joe (DuckCorp) {verbs.Conversation.PUBLIC_MESSAGE}",
                "my content",
            ),
        ),
        (
            verbs.Conversation.PRIVATE_MESSAGE,
            private_note,
            (
                f"Bobi Joe (DuckCorp) {verbs.Conversation.PRIVATE_MESSAGE}",
                "my content",
            ),
        ),
        (
            verbs.Recommendation.COMMENTED,
            followup,
            (
                f"Bobi Joe (DuckCorp) {verbs.Recommendation.COMMENTED} 'Belle Ressource'",
                followup.comment,
            ),
        ),
        (
            verbs.Recommendation.CREATED,
            task,
            (
                f"Bobi Joe (DuckCorp) {verbs.Recommendation.CREATED} 'Belle Ressource'",
                task.content,
            ),
        ),
        (
            verbs.Project.BECAME_ADVISOR,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.BECAME_ADVISOR}.",
                None,
            ),
        ),
        (
            verbs.Project.BECAME_OBSERVER,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.BECAME_OBSERVER}.",
                None,
            ),
        ),
        (
            verbs.Project.SUBMITTED_BY,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.SUBMITTED_BY}: 'Nice Project'",
                "Super description",
            ),
        ),
        (
            verbs.Project.AVAILABLE,  # FIXME redondant avec VALIDATED
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.AVAILABLE} 'Nice Project'",
                "Super description",
            ),
        ),
        (
            verbs.Document.ADDED,  # FIXME replace w/ ADDED_FILE ADDED_LINK
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Document.ADDED}",
                None,
            ),
        ),
        (
            "action inconnue",
            project,
            (
                "Bob action inconnue Nice Project - SomeWhere",
                None,
            ),
        ),
    ]

    for t in tests:
        notify.send(
            sender=user,
            recipient=recipient,
            verb=t[0],
            action_object=t[1],
            target=project,
        )

    for idx, notification in enumerate(
        reversed(notifications_models.Notification.objects.all())
    ):
        fmt_reco = formatter.format(notification)
        assert tests[idx][2][0] == fmt_reco.summary
        assert tests[idx][2][1] == fmt_reco.excerpt


@pytest.mark.django_db
def test_notification_formatter_with_bogus_user():
    formatter = digests.NotificationFormatter()

    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    note = Recipe(projects_models.Note).make()

    notification = Notification(
        user, verb=verbs.Conversation.PUBLIC_MESSAGE, action_object=note
    )

    fmt_reco = formatter.format(notification)
    assert "compte indisponible" in str(fmt_reco)


# eof
