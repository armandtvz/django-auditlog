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

        if hasattr(instance, 'org'):
            print('post_delete - ' + instance._meta.model_name + str(instance.org))

        # TODO DRY
        log_created.send(
            sender=LogEntry,
            old_instance=instance,
            new_instance=None,
            log_instance=log_entry,
        )


def log_pre_delete(sender, instance, **kwargs):
    if hasattr(instance, 'org'):
        print('pre_delete - ' + instance._meta.model_name + str(instance.org))
