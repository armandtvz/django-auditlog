import json

from auditlog.diff import model_instance_diff
from auditlog.models import LogEntry
from auditlog.signals import log_created


def log_create(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if created:
        changes = model_instance_diff(None, instance)

        log_entry = LogEntry.objects.log_create(
            instance,
            action=LogEntry.Action.CREATE,
            changes=json.dumps(changes),
        )
        # TODO DRY
        log_created.send(
            sender=LogEntry,
            old_instance=None,
            new_instance=instance,
            log_instance=log_entry,
        )

def log_update(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            new = instance

            changes = model_instance_diff(old, new)

            # Log an entry only if there are changes
            if changes:
                log_entry = LogEntry.objects.log_create(
                    instance,
                    action=LogEntry.Action.UPDATE,
                    changes=json.dumps(changes),
                )
                # TODO DRY
                log_created.send(
                    sender=LogEntry,
                    old_instance=old,
                    new_instance=new,
                    log_instance=log_entry,
                )


def log_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)

        log_entry = LogEntry.objects.log_create(
            instance,
            action=LogEntry.Action.DELETE,
            changes=json.dumps(changes),
        )
        log_created.send(
            sender=LogEntry,
            old_instance=instance,
            new_instance=None,
            log_instance=log_entry,
        )

def make_log_m2m_changes(field_name):
    """Return a handler for m2m_changed with field_name enclosed."""

    def log_m2m_changes(signal, action, **kwargs):
        """Handle m2m_changed and call LogEntry.objects.log_m2m_changes as needed."""
        if action not in ["post_add", "post_clear", "post_remove"]:
            return

        if action == "post_clear":
            changed_queryset = kwargs["model"].objects.all()
        else:
            changed_queryset = kwargs["model"].objects.filter(pk__in=kwargs["pk_set"])

        if action in ["post_add"]:
            LogEntry.objects.log_m2m_changes(
                changed_queryset,
                kwargs["instance"],
                "add",
                field_name,
            )
        elif action in ["post_remove", "post_clear"]:
            LogEntry.objects.log_m2m_changes(
                changed_queryset,
                kwargs["instance"],
                "delete",
                field_name,
            )

    return log_m2m_changes
