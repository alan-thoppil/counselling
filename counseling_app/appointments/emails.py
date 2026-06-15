import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_appointment_email(appointment, action):
    """Sends email notifications for appointment activities (booking, confirmation, cancellation)"""
    subject = f"Aura Appointment {action.capitalize()}: {appointment.date} at {appointment.time}"
    
    if action == 'booked':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment with Therapist {appointment.therapist.username} has been requested for "
            f"{appointment.date} at {appointment.time}.\n\n"
            f"Reason: {appointment.reason or 'None'}\n"
            f"Status: {appointment.status.capitalize()}\n\n"
            f"Thank you for choosing Aura!\n"
            f"Aura Support Team"
        )
    elif action == 'cancelled':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment with Therapist {appointment.therapist.username} on "
            f"{appointment.date} at {appointment.time} has been successfully cancelled.\n\n"
            f"If this was a mistake, please visit the dashboard to schedule a new session.\n\n"
            f"Thank you,\n"
            f"Aura Support Team"
        )
    else:
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment status with Therapist {appointment.therapist.username} is now "
            f"updated to '{appointment.status.capitalize()}'.\n\n"
            f"Aura Support Team"
        )

    recipient_list = []
    if appointment.patient.email:
        recipient_list.append(appointment.patient.email)
    if appointment.therapist.email:
        recipient_list.append(appointment.therapist.email)

    if not recipient_list:
        # Fallback logging if no email addresses exist for test users
        logger.info(f"[Email simulation] No email addresses set. Log of message:\n"
                    f"Subject: {subject}\n"
                    f"Recipient List: {[appointment.patient.username, appointment.therapist.username]}\n"
                    f"Body:\n{message}\n")
        
        # Still attempt to send to default console in development to verify backend is working
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@aura.com'),
                recipient_list=['test@example.com'], # mock list to trigger print to console
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to print simulated mail to console: {e}")
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@aura.com'),
            recipient_list=recipient_list,
            fail_silently=True
        )
        logger.info(f"Successfully sent appointment {action} email to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to dispatch appointment email: {e}")
