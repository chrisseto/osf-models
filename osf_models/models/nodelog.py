from django.apps import apps
from django.db import models
from django.utils import timezone

from website.util import api_v2_url

from osf_models.models.base import BaseModel, ObjectIDMixin
from osf_models.utils.datetime_aware_jsonfield import DateTimeAwareJSONField


class NodeLog(ObjectIDMixin, BaseModel):
    # TODO DELETE ME POST MIGRATION
    modm_model_path = 'website.project.model.NodeLog'
    modm_query = None
    migration_page_size = 100000
    # /TODO DELETE ME POST MIGRATION
    DATE_FORMAT = '%m/%d/%Y %H:%M UTC'

    # Log action constants -- NOTE: templates stored in log_templates.mako
    CREATED_FROM = 'created_from'

    PROJECT_CREATED = 'project_created'
    PROJECT_REGISTERED = 'project_registered'
    PROJECT_DELETED = 'project_deleted'

    NODE_CREATED = 'node_created'
    NODE_FORKED = 'node_forked'
    NODE_REMOVED = 'node_removed'

    POINTER_CREATED = NODE_LINK_CREATED = 'pointer_created'
    POINTER_FORKED = NODE_LINK_FORKED = 'pointer_forked'
    POINTER_REMOVED = NODE_LINK_REMOVED = 'pointer_removed'

    WIKI_UPDATED = 'wiki_updated'
    WIKI_DELETED = 'wiki_deleted'
    WIKI_RENAMED = 'wiki_renamed'

    MADE_WIKI_PUBLIC = 'made_wiki_public'
    MADE_WIKI_PRIVATE = 'made_wiki_private'

    CONTRIB_ADDED = 'contributor_added'
    CONTRIB_REMOVED = 'contributor_removed'
    CONTRIB_REORDERED = 'contributors_reordered'

    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'

    PERMISSIONS_UPDATED = 'permissions_updated'

    MADE_PRIVATE = 'made_private'
    MADE_PUBLIC = 'made_public'

    TAG_ADDED = 'tag_added'
    TAG_REMOVED = 'tag_removed'

    FILE_TAG_ADDED = 'file_tag_added'
    FILE_TAG_REMOVED = 'file_tag_removed'

    EDITED_TITLE = 'edit_title'
    EDITED_DESCRIPTION = 'edit_description'
    CHANGED_LICENSE = 'license_changed'

    UPDATED_FIELDS = 'updated_fields'

    FILE_MOVED = 'addon_file_moved'
    FILE_COPIED = 'addon_file_copied'
    FILE_RENAMED = 'addon_file_renamed'

    FOLDER_CREATED = 'folder_created'

    FILE_ADDED = 'file_added'
    FILE_UPDATED = 'file_updated'
    FILE_REMOVED = 'file_removed'
    FILE_RESTORED = 'file_restored'

    ADDON_ADDED = 'addon_added'
    ADDON_REMOVED = 'addon_removed'
    COMMENT_ADDED = 'comment_added'
    COMMENT_REMOVED = 'comment_removed'
    COMMENT_UPDATED = 'comment_updated'
    COMMENT_RESTORED = 'comment_restored'

    CITATION_ADDED = 'citation_added'
    CITATION_EDITED = 'citation_edited'
    CITATION_REMOVED = 'citation_removed'

    MADE_CONTRIBUTOR_VISIBLE = 'made_contributor_visible'
    MADE_CONTRIBUTOR_INVISIBLE = 'made_contributor_invisible'

    EXTERNAL_IDS_ADDED = 'external_ids_added'

    EMBARGO_APPROVED = 'embargo_approved'
    EMBARGO_CANCELLED = 'embargo_cancelled'
    EMBARGO_COMPLETED = 'embargo_completed'
    EMBARGO_INITIATED = 'embargo_initiated'
    EMBARGO_TERMINATED = 'embargo_terminated'

    RETRACTION_APPROVED = 'retraction_approved'
    RETRACTION_CANCELLED = 'retraction_cancelled'
    RETRACTION_INITIATED = 'retraction_initiated'

    REGISTRATION_APPROVAL_CANCELLED = 'registration_cancelled'
    REGISTRATION_APPROVAL_INITIATED = 'registration_initiated'
    REGISTRATION_APPROVAL_APPROVED = 'registration_approved'
    PREREG_REGISTRATION_INITIATED = 'prereg_registration_initiated'

    AFFILIATED_INSTITUTION_ADDED = 'affiliated_institution_added'
    AFFILIATED_INSTITUTION_REMOVED = 'affiliated_institution_removed'

    actions = [CHECKED_IN, CHECKED_OUT, FILE_TAG_REMOVED, FILE_TAG_ADDED, CREATED_FROM, PROJECT_CREATED,
               PROJECT_REGISTERED, PROJECT_DELETED, NODE_CREATED, NODE_FORKED, NODE_REMOVED,
               NODE_LINK_CREATED, NODE_LINK_FORKED, NODE_LINK_REMOVED, WIKI_UPDATED,
               WIKI_DELETED, WIKI_RENAMED, MADE_WIKI_PUBLIC,
               MADE_WIKI_PRIVATE, CONTRIB_ADDED, CONTRIB_REMOVED, CONTRIB_REORDERED,
               PERMISSIONS_UPDATED, MADE_PRIVATE, MADE_PUBLIC, TAG_ADDED, TAG_REMOVED, EDITED_TITLE,
               EDITED_DESCRIPTION, UPDATED_FIELDS, FILE_MOVED, FILE_COPIED,
               FOLDER_CREATED, FILE_ADDED, FILE_UPDATED, FILE_REMOVED, FILE_RESTORED, ADDON_ADDED,
               ADDON_REMOVED, COMMENT_ADDED, COMMENT_REMOVED, COMMENT_UPDATED, MADE_CONTRIBUTOR_VISIBLE,
               MADE_CONTRIBUTOR_INVISIBLE, EXTERNAL_IDS_ADDED, EMBARGO_APPROVED, EMBARGO_TERMINATED,
               EMBARGO_CANCELLED, EMBARGO_COMPLETED, EMBARGO_INITIATED, RETRACTION_APPROVED,
               RETRACTION_CANCELLED, RETRACTION_INITIATED, REGISTRATION_APPROVAL_CANCELLED,
               REGISTRATION_APPROVAL_INITIATED, REGISTRATION_APPROVAL_APPROVED, PREREG_REGISTRATION_INITIATED,
               CITATION_ADDED, CITATION_EDITED, CITATION_REMOVED,
               AFFILIATED_INSTITUTION_ADDED, AFFILIATED_INSTITUTION_REMOVED]
    action_choices = [(action, action.upper()) for action in actions]
    date = models.DateTimeField(default=timezone.now, db_index=True,
                                null=True, blank=True)  # auto_now_add=True)
    action = models.CharField(max_length=255, db_index=True, choices=action_choices)
    params = DateTimeAwareJSONField(default=dict)
    should_hide = models.BooleanField(default=False)
    user = models.ForeignKey('OSFUser', related_name='logs', db_index=True, null=True, blank=True)
    foreign_user = models.CharField(max_length=255, null=True, blank=True)
    node = models.ForeignKey('AbstractNode', related_name='logs', db_index=True, null=True, blank=True)
    original_node = models.ForeignKey('AbstractNode', db_index=True, null=True, blank=True)

    def __unicode__(self):
        return u'{} on {} by {} at {}'.format(self.action, self.node._id, self.user._id, self.date)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    @property
    def absolute_api_v2_url(self):
        path = '/logs/{}/'.format(self._id)
        return api_v2_url(path)

    def get_absolute_url(self):
        return self.absolute_api_v2_url

    @property
    def absolute_url(self):
        return self.absolute_api_v2_url

    def clone_node_log(self, node_id):
        """
        When a node is forked or registered, all logs on the node need to be
        cloned for the fork or registration.

        :param node_id:
        :return: cloned log
        """
        AbstractNode = apps.get_model('osf_models.AbstractNode')
        original_log = self.load(self._id)
        node = AbstractNode.load(node_id)
        log_clone = original_log.clone()
        log_clone.node = node
        log_clone.original_node = original_log.original_node
        log_clone.user = original_log.user
        log_clone.save()
        return log_clone
