import logging
import requests
import json

from datetime import datetime
from pyodk.client import Client

log = logging.getLogger("app")

client = Client(config_path="./config.toml")


def get_attachment(project_id, form_id, uuid_sub, media_name):
    print(
        "URL BIS##################",
        f"projects/{project_id}/forms/{form_id}/submissions/{uuid_sub}/attachments/{media_name}",
    )
    img = client.get(
        f"projects/{project_id}/forms/{form_id}/submissions/{uuid_sub}/attachments/{media_name}"
    )
    return img


def get_submissions(project_id, form_id):
    # Creation client odk central
    form_data = None
    with client:
        form_data = client.submissions.get_table(
            form_id=form_id,
            project_id=project_id,
            expand="*",
            # filter="__system/submissionDate ge 2022-12-06T14:56:00.000Z"
            # filter= "__system/reviewState not rejected"
        )
        return form_data["value"]


def get_attachments(project_id, form_data):
    # #########################################
    #  Attachments
    # projects/1/forms/Sicen/submissions/{data['__id']}/attachments => Récupération de la liste des attachments pour une soumissions
    # projects/1/forms/Sicen/submissions/{data['__id']}/attachments/{att['name']} => Téléchargement de l'attachment pour la soumission
    for data in form_data:
        attachments_list = client.get(
            f"projects/1/forms/Sicen/submissions/{data['__id']}/attachments"
        )
        print("Nombre de médias", {data["__id"]}, len(attachments_list.json()))
        print(attachments_list.json())
        for att in attachments_list.json():
            img = client.get(
                f"projects/{project_id}/forms/Sicen/submissions/{data['__id']}/attachments/{att['name']}"
            )
            print(
                "URL###################",
                f"projects/{project_id}/forms/Sicen/submissions/{data['__id']}/attachments/{att['name']}",
            )
            with open(att["name"], "wb") as out_file:
                out_file.write(img.content)

    assert response.status_code == 200


def update_review_state(project_id, xml_form_id, submission_id):

    review_states = ["approved", "hasIssues", "rejected"]
    token = client.auth.get_token(
            username=client.config.central.username,
            password=client.config.central.password,
        )
    review_submission_response = requests.patch(
        f"{client.config.central.base_url}/v1/projects/{project_id}/forms/{xml_form_id}/submissions/{submission_id}",
        data=json.dumps({"reviewState": review_states[2]}),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
    )
    print(review_submission_response.json())

def update_form_attachment(project_id, xml_form_id, files):
    """Mise à jour du formulaires
        3 étapes :
         1 - passer le formulaire en draft
         2 - mettre à jour les médias
         3 - publier le formulaires
    :param project_id: id du projet
    :type project_id: int
    :param xml_form_id: nom du formulaire
    :type xml_form_id: str
    :param files: dictionnaires des fichiers à poster
    :type files: dict
    """
    form_draft(project_id, xml_form_id)
    for file_name in files:
        upload_form_attachment(project_id, xml_form_id, file_name=file_name, data=files[file_name])
    publish_form(project_id, xml_form_id)


def form_draft(project_id, xml_form_id):
    """Publie une ébauche du formulaire

    TODO : mette à jour la définition du formulaire

    :param project_id: id du projet
    :type project_id: int
    :param xml_form_id: nom du formulaire
    :type xml_form_id: str
    """
    with client:
        request = client.post(f"projects/{project_id}/forms/{xml_form_id}/draft")
        assert request.status_code == 200

def upload_form_attachment(project_id, xml_form_id, file_name, data):
    """Upload fichier attaché du formulaire

    :param project_id: id du projet
    :type project_id: int
    :param xml_form_id: nom du formulaire
    :type xml_form_id: str
    :param file_name: nom du fichier
    :type file_name: str
    :param data: csv data converti en chaine de caractères
    :type data: str
    """
    response = client.post(
        f"{client.config.central.base_url}/v1/projects/{project_id}/forms/{xml_form_id}/draft/attachments/{file_name}",
        data=data.encode("utf-8", "strict")
    )
    if response.status_code == 404:
        log.warning(f"Le fichier {file_name} n'existe pas dans la définition du formulaire")
    elif response.status_code == 200:
        log.info(f"fichier {file_name} téléversé")
    else:
        #TODO raise error
        pass


def publish_form(project_id, xml_form_id):
    """Publication du formulaire avec un nouveau numéro de version
        :param project_id: id du projet
    :type project_id: int
    :param xml_form_id: nom du formulaire
    :type xml_form_id: str
    """
    version_number = datetime.now()
    response = client.post(f"projects/{project_id}/forms/{xml_form_id}/draft/publish?version={version_number}")
    assert response.status_code == 200


def get_schema_fields(project_id, xml_form_id):
    resp = client.get(f"projects/{project_id}/forms/{xml_form_id}/fields?odata=false")
    return resp.json()


class ODKSchema:
    def __init__(self, project_id, form_id):
        self.project_id = project_id
        self.form_id = form_id
        self.schema = self._get_schema_fields()

    def _get_schema_fields(self):
        with client:
            resp = client.get(
                f"projects/{self.project_id}/forms/{self.form_id}/fields?odata=false"
            )
            assert resp.status_code == 200
            return resp.json()

    def get_field_info(self, field_name):
        try:
            return next(field for field in self.schema if field["name"] == field_name)
        except StopIteration:
            log.error(f"the field {field_name} does not exist in this ODK form")
            raise