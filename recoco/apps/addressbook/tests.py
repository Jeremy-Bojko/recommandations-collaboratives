import pytest
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from recoco.utils import login

from . import models

########################################################################################
# Organization
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_organization_not_available_for_non_staff(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_organization_available_for_staff(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_new_organization_and_redirect(request, client):
    site = get_current_site(request)
    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    organization = models.Organization.on_site.first()
    assert organization.name == data["name"]
    assert site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_list_not_available_for_non_staff(client):
    url = reverse("addressbook-organization-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_existing_organization_and_redirect(request, client):
    current_site = get_current_site(request)

    organization = Recipe(
        models.Organization, sites=[current_site], name="my organization"
    ).make()
    assert organization.sites.count() == 1

    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    # no new organization created
    assert models.Organization.on_site.count() == 1

    updated = models.Organization.on_site.first()
    assert updated.name == data["name"]
    assert organization.sites.count() == 1
    assert current_site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_create_existing_organization_on_other_site_and_redirect(request, client):
    current_site = get_current_site(request)
    other_site = baker.make(sites_models.Site)

    organization = Recipe(
        models.Organization, sites=[other_site], name="my organization"
    ).make()
    assert organization.sites.count() == 1

    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    # no new organization created
    assert models.Organization.on_site.count() == 1

    updated = models.Organization.on_site.first()
    assert updated.name == data["name"]
    assert organization.sites.count() == 2
    assert current_site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_create_error(client):
    url = reverse("addressbook-organization-create")

    data = {}
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert models.Organization.on_site.count() == 0

    assert response.status_code == 200


# Listing


@pytest.mark.django_db
def test_organization_list_not_available_for_non_switchtender(client):
    url = reverse("addressbook-organization-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_organization_list_available_for_switchtender(client):
    url = reverse("addressbook-organization-list")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_organization_list_only_contains_site_org_w_contacts(request, client):
    site = get_current_site(request)
    other = baker.make(sites_models.Site)

    on_site_no_contacts = Recipe(
        models.Organization, name="no_contacts", sites=[site]
    ).make()
    other_site = Recipe(models.Organization, name="other_site", sites=[other]).make()
    no_site = Recipe(models.Organization, name="no_site", sites=[]).make()

    on_site_w_contacts = Recipe(
        models.Organization, name="on_site_w_contacts", sites=[site]
    ).make()
    baker.make(models.Contact, organization=on_site_w_contacts, site=site)

    url = reverse("addressbook-organization-list")

    with settings.SITE_ID.override(site.pk):
        with login(client, groups=["example_com_staff"]):
            response = client.get(url)

    assert response.status_code == 200

    assertContains(response, on_site_w_contacts.name)
    assertNotContains(response, on_site_no_contacts.name)
    assertNotContains(response, other_site.name)
    assertNotContains(response, no_site.name)


#
# update


@pytest.mark.django_db
def test_update_organization_not_available_for_non_switchtender_users(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_organization_available_for_switchtender(request, client):
    current_site = get_current_site(request)

    organization = Recipe(models.Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-organization-update"')


@pytest.mark.django_db
def test_organization_update_and_redirect(request, client):
    current_site = get_current_site(request)

    organization = Recipe(models.Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    with login(client, groups=["example_com_staff"]):
        data = {"name": "new name", "departments": []}
        response = client.post(url, data=data)

    updated_organization = models.Organization.on_site.get(id=organization.id)
    assert updated_organization.name == data["name"]

    new_url = reverse("addressbook-organization-list")
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_update_error(request, client):
    current_site = get_current_site(request)

    organization = Recipe(models.Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    data = {}
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    updated_organization = models.Organization.on_site.get(id=organization.id)
    assert updated_organization.name == organization.name

    assert response.status_code == 200


########################################################################################
# Contact
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_contact_not_available_for_non_switchtender(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_contact_available_for_switchtender(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-create"')


@pytest.mark.django_db
def test_contact_create_and_redirect(request, client):
    current_site = get_current_site(request)

    organization = Recipe(models.Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-contact-create", args=[organization.id])

    with login(client, groups=["example_com_staff"]):
        data = {"first_name": "my contact"}
        response = client.post(url, data=data)

    contact = models.Contact.on_site.all()[0]
    assert contact.first_name == data["first_name"]

    new_url = reverse("addressbook-organization-details", args=[organization.id])
    assertRedirects(response, new_url)


#
# update


@pytest.mark.django_db
def test_update_contact_not_available_for_non_switchtender(client):
    contact = Recipe(models.Contact).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_contact_available_for_switchtender(request, client):
    contact = Recipe(models.Contact, site=get_current_site(request)).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-update"')


@pytest.mark.django_db
def test_contact_update_and_redirect(request, client):
    current_site = get_current_site(request)

    contact = Recipe(
        models.Contact, organization__sites=[current_site], site=current_site
    ).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])

    with login(client, groups=["example_com_staff"]):
        data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "division": "division",
            "phone_no": "phone_no",
            "mobile_no": "mobile_no",
        }
        response = client.post(url, data=data)

    updated_contact = models.Contact.on_site.get(id=contact.id)
    assert updated_contact.first_name == data["first_name"]

    new_url = reverse(
        "addressbook-organization-details", args=[contact.organization_id]
    )
    assertRedirects(response, new_url)


########################################################################
# REST API: searching organizations
########################################################################


@pytest.mark.django_db
def test_anonymous_can_use_organization_api(client):
    url = reverse("organizations-list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_can_search_organization_api(client, request):
    current_site = get_current_site(request)

    baker.make(models.Organization, name="acme corporation", sites=[current_site])

    url = reverse("organizations-list")
    response = client.get(url, {"search": "acme"}, format="json")

    assert response.status_code == 200
    assert len(response.data) > 0


# eof
